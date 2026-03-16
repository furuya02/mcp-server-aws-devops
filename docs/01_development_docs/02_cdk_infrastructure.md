# CDK インフラストラクチャ設計

## 概要

本プロジェクトは AWS CDK (Cloud Development Kit) を使用してインフラストラクチャをコードとして管理しています。TypeScript で記述され、認証方式の切り替えに対応した柔軟な構成となっています。

## CDK プロジェクト構成

```
cdk/
├── bin/
│   └── cdk.ts              # CDK アプリケーションエントリーポイント
├── lib/
│   └── mcp-stack.ts        # メインスタック定義
├── lambda_python/
│   ├── index.py            # Lambda 関数実装
│   └── requirements.txt    # Python 依存関係
├── cdk.json                # CDK 設定・コンテキスト
├── package.json            # Node.js 依存関係
└── tsconfig.json           # TypeScript 設定
```

## 主要ファイル

### bin/cdk.ts

CDK アプリケーションのエントリーポイントです。

```typescript
const projectName = app.node.tryGetContext('projectName') || 'mcp-server-sample';
const authType = app.node.tryGetContext('authType') || 'api-key';

// authType の検証
if (authType !== 'api-key' && authType !== 'oauth') {
  throw new Error(`Invalid authType: ${authType}. Must be 'api-key' or 'oauth'`);
}
```

**機能:**
- コンテキストパラメータの読み取り
- 認証タイプの検証
- スタックのインスタンス化

### lib/mcp-stack.ts

メインの CDK スタック定義です。

**スタックプロパティ:**

```typescript
export interface McpStackProps extends cdk.StackProps {
  projectName: string;           // プロジェクト名（リソース命名に使用）
  authType: 'api-key' | 'oauth'; // 認証タイプ
}
```

**作成されるリソース:**
- Lambda 関数
- API Gateway REST API
- 認証関連リソース（API Key または Cognito）

## コンテキストパラメータ

### cdk.json

```json
{
  "context": {
    "projectName": "mcp-server-sample",
    "authType": "api-key"
  }
}
```

| パラメータ | 型 | デフォルト | 説明 |
|-----------|------|---------|------|
| `projectName` | string | `mcp-server-sample` | リソース命名に使用 |
| `authType` | string | `api-key` | 認証方式 (`api-key` または `oauth`) |

### コマンドラインでの上書き

```bash
# API Key 認証（デフォルト）
npx cdk deploy

# OAuth 認証
npx cdk deploy -c authType=oauth

# カスタムプロジェクト名
npx cdk deploy -c projectName=my-mcp-server

# 両方指定
npx cdk deploy -c projectName=my-mcp-server -c authType=oauth
```

## Lambda 関数の定義

```typescript
const mcpFunction = new lambda.Function(this, 'McpFunction', {
  functionName: `${projectName}-mcp`,
  runtime: lambda.Runtime.PYTHON_3_12,
  handler: 'index.handler',
  code: lambda.Code.fromAsset(path.join(__dirname, '../lambda_python'), {
    bundling: {
      image: lambda.Runtime.PYTHON_3_12.bundlingImage,
      command: [
        'bash', '-c',
        'pip install -r requirements.txt -t /asset-output && cp -r . /asset-output',
      ],
    },
  }),
  architecture: lambda.Architecture.X86_64,
  timeout: cdk.Duration.seconds(600),
  memorySize: 256,
  tracing: lambda.Tracing.ACTIVE,
});
```

**構成詳細:**

| 設定 | 値 | 説明 |
|------|-----|------|
| ランタイム | Python 3.12 | Lambda 実行環境 |
| アーキテクチャ | x86_64 | CPU アーキテクチャ |
| タイムアウト | 600 秒 | 最大実行時間 |
| メモリ | 256 MB | 割り当てメモリ |
| トレーシング | Active | X-Ray 有効 |

**バンドリング:**
- Docker を使用して Python 依存関係をインストール
- `requirements.txt` の依存関係を含める

## API Gateway の定義

```typescript
const mcpApi = new apigateway.RestApi(this, 'McpApi', {
  restApiName: `${projectName}-api`,
  description: `MCP API with Streamable HTTP and ${authType} authentication`,
  deployOptions: {
    stageName: 'prd',
    tracingEnabled: true,
  },
  defaultCorsPreflightOptions: {
    allowOrigins: apigateway.Cors.ALL_ORIGINS,
    allowMethods: apigateway.Cors.ALL_METHODS,
  },
  apiKeySourceType: authType === 'api-key'
    ? apigateway.ApiKeySourceType.HEADER
    : undefined,
});
```

**構成詳細:**

| 設定 | 値 | 説明 |
|------|-----|------|
| ステージ名 | `prd` | デプロイステージ |
| トレーシング | 有効 | X-Ray 統合 |
| CORS | 全オリジン許可 | クロスオリジン設定 |

## 認証方式別の構成

### API Key 認証

```typescript
// API Key
const apiKey = new apigateway.ApiKey(this, 'McpApiKey', {
  apiKeyName: `${projectName}-api-key`,
  description: 'API Key for MCP API',
  enabled: true,
});

// Usage Plan
const usagePlan = new apigateway.UsagePlan(this, 'McpUsagePlan', {
  name: `${projectName}-usage-plan`,
  apiStages: [{ api: mcpApi, stage: mcpApi.deploymentStage }],
  throttle: {
    rateLimit: 100,
    burstLimit: 200,
  },
});

usagePlan.addApiKey(apiKey);
```

### OAuth 認証

```typescript
// Cognito User Pool
const userPool = new cognito.UserPool(this, 'McpUserPool', {
  userPoolName: `${projectName}-user-pool`,
  selfSignUpEnabled: false,
  removalPolicy: cdk.RemovalPolicy.DESTROY,
});

// Cognito Domain
const userPoolDomain = userPool.addDomain('McpUserPoolDomain', {
  cognitoDomain: {
    domainPrefix: `${projectName}-${cdk.Aws.ACCOUNT_ID}`.toLowerCase(),
  },
});

// Resource Server
const resourceServer = userPool.addResourceServer('McpResourceServer', {
  identifier: `${projectName}-api`,
  scopes: [{ scopeName: 'mcp.invoke', scopeDescription: 'Invoke MCP tools' }],
});

// App Client
const appClient = userPool.addClient('McpAppClient', {
  userPoolClientName: `${projectName}-app-client`,
  generateSecret: true,
  oAuth: {
    flows: { clientCredentials: true },
    scopes: [cognito.OAuthScope.resourceServer(resourceServer, { ... })],
  },
  accessTokenValidity: cdk.Duration.hours(1),
});

// Cognito Authorizer
const cognitoAuthorizer = new apigateway.CognitoUserPoolsAuthorizer(this, 'McpCognitoAuthorizer', {
  cognitoUserPools: [userPool],
  identitySource: 'method.request.header.Authorization',
});
```

## CloudFormation 出力

### 共通出力

| 出力名 | 説明 |
|-------|------|
| `McpFunctionArn` | Lambda 関数の ARN |
| `McpApiUrl` | API Gateway のベース URL |
| `McpApiEndpoint` | MCP エンドポイント URL |
| `AuthType` | 使用中の認証タイプ |

### API Key 認証時の追加出力

| 出力名 | 説明 |
|-------|------|
| `ApiKeyId` | API Key ID |
| `GetApiKeyCommand` | API Key 値取得コマンド |

### OAuth 認証時の追加出力

| 出力名 | 説明 |
|-------|------|
| `UserPoolId` | Cognito User Pool ID |
| `AppClientId` | Cognito App Client ID |
| `TokenEndpoint` | OAuth 2.0 Token Endpoint |
| `OAuthScope` | 使用するスコープ |
| `GetClientSecretCommand` | Client Secret 取得コマンド |

## 依存関係

### package.json

```json
{
  "dependencies": {
    "aws-cdk-lib": "2.238.0",
    "constructs": "^10.0.0"
  },
  "devDependencies": {
    "@types/node": "20.14.9",
    "ts-node": "^10.9.2",
    "typescript": "~5.4.0"
  }
}
```

## ベストプラクティス

### セキュリティ

- API Key 値は出力せず、取得コマンドを提供
- Client Secret は AWS CLI で取得
- 認証情報をコードに含めない

### 運用

- スタック削除時のリソース削除設定 (`RemovalPolicy.DESTROY`)
- X-Ray トレーシング有効化
- ログ収集設定

### 開発

- TypeScript による型安全性
- コンテキストパラメータによる柔軟な設定
- Docker バンドリングによる依存関係管理
