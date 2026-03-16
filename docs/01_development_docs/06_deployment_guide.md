# デプロイガイド

## 前提条件

### 必要なソフトウェア

| ソフトウェア | バージョン | 用途 |
|-------------|-----------|------|
| Node.js | 18+ | CDK 実行環境 |
| Docker | 最新版 | Lambda 関数のバンドリング |
| AWS CLI | 2.x | AWS リソースへのアクセス |
| pnpm または npm | 最新版 | パッケージ管理 |

### AWS 認証情報

AWS CLI が設定済みで、以下の権限が必要です：

- Lambda
- API Gateway
- Cognito（OAuth 認証の場合）
- CloudFormation
- IAM

## デプロイ手順

### 1. 依存関係のインストール

```bash
cd cdk
pnpm install
# または
npm install
```

### 2. CDK Bootstrap（初回のみ）

AWS アカウントで CDK を初めて使用する場合は、Bootstrap が必要です。

```bash
npx cdk bootstrap
```

### 3. デプロイ

#### API Key 認証（デフォルト）

```bash
npx cdk deploy
```

#### OAuth 認証

```bash
npx cdk deploy -c authType=oauth
```

#### カスタムプロジェクト名

```bash
npx cdk deploy -c projectName=my-mcp-server
```

#### 両方指定

```bash
npx cdk deploy -c projectName=my-mcp-server -c authType=oauth
```

### 4. 出力値の確認

デプロイ完了後、CloudFormation の出力値を確認します。

**共通出力:**
```
Outputs:
McpStack.McpFunctionArn = arn:aws:lambda:ap-northeast-1:123456789012:function:mcp-server-sample-mcp
McpStack.McpApiUrl = https://xxxxxxxxxx.execute-api.ap-northeast-1.amazonaws.com/prd/
McpStack.McpApiEndpoint = https://xxxxxxxxxx.execute-api.ap-northeast-1.amazonaws.com/prd/mcp
McpStack.AuthType = api-key
```

## デプロイ後の作業

### API Key 認証の場合

#### API Key の取得

```bash
# 出力された GetApiKeyCommand を実行
aws apigateway get-api-key \
  --api-key {ApiKeyId} \
  --include-value \
  --query 'value' \
  --output text
```

### OAuth 認証の場合

#### Client Secret の取得

```bash
# 出力された GetClientSecretCommand を実行
aws cognito-idp describe-user-pool-client \
  --user-pool-id {UserPoolId} \
  --client-id {AppClientId} \
  --query 'UserPoolClient.ClientSecret' \
  --output text
```

#### アクセストークンの取得

```bash
curl -X POST "{TokenEndpoint}" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -u "{AppClientId}:{ClientSecret}" \
  -d "grant_type=client_credentials&scope={OAuthScope}"
```

## 動作確認

### MCP Inspector を使用

```bash
# API Key 認証
npx @modelcontextprotocol/inspector \
  --transport streamable-http \
  --url "{McpApiEndpoint}" \
  --header "x-api-key: {API_KEY}"

# OAuth 認証
npx @modelcontextprotocol/inspector \
  --transport streamable-http \
  --url "{McpApiEndpoint}" \
  --header "Authorization: Bearer {ACCESS_TOKEN}"
```

### curl を使用

#### tools/list の呼び出し

```bash
# API Key 認証
curl -X POST "{McpApiEndpoint}" \
  -H "x-api-key: {API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }'

# OAuth 認証
curl -X POST "{McpApiEndpoint}" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }'
```

#### get_schedule ツールの呼び出し

```bash
curl -X POST "{McpApiEndpoint}" \
  -H "x-api-key: {API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "get_schedule",
      "arguments": {}
    },
    "id": 2
  }'
```

## スタックの更新

コードを変更した後、再度デプロイします。

```bash
npx cdk deploy
```

## スタックの削除

```bash
npx cdk destroy
```

**注意:** 削除前に確認プロンプトが表示されます。

## トラブルシューティング

### Docker が起動していない

```
Error: Cannot connect to the Docker daemon
```

**解決策:** Docker Desktop を起動してください。

### CDK Bootstrap が未実行

```
Error: This stack uses assets, so the toolkit stack must be deployed to the environment
```

**解決策:** `npx cdk bootstrap` を実行してください。

### 権限エラー

```
Error: User: arn:aws:iam::... is not authorized to perform: ...
```

**解決策:** AWS CLI の認証情報に必要な権限があることを確認してください。

### Cognito ドメインの重複（OAuth）

```
Error: Domain already associated with another user pool
```

**解決策:** プロジェクト名を変更するか、既存のドメインを削除してください。

## CI/CD 統合

### GitHub Actions の例

```yaml
name: Deploy MCP Server

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        run: |
          cd cdk
          npm install

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ap-northeast-1

      - name: Deploy
        run: |
          cd cdk
          npx cdk deploy --require-approval never
```

## 環境別デプロイ

### 開発環境

```bash
npx cdk deploy -c projectName=mcp-server-dev
```

### ステージング環境

```bash
npx cdk deploy -c projectName=mcp-server-stg
```

### 本番環境

```bash
npx cdk deploy -c projectName=mcp-server-prd
```
