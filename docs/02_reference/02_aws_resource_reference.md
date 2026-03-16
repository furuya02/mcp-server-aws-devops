# AWS リソースリファレンス

## 概要

本プロジェクトでデプロイされる AWS リソースの一覧と詳細設定です。

## リソース一覧

### 共通リソース

| リソース | 論理ID | 物理名 | 説明 |
|---------|--------|--------|------|
| Lambda Function | McpFunction | `{projectName}-mcp` | MCP Server |
| REST API | McpApi | `{projectName}-api` | API Gateway |

### API Key 認証時の追加リソース

| リソース | 論理ID | 物理名 | 説明 |
|---------|--------|--------|------|
| API Key | McpApiKey | `{projectName}-api-key` | API キー |
| Usage Plan | McpUsagePlan | `{projectName}-usage-plan` | 使用量プラン |

### OAuth 認証時の追加リソース

| リソース | 論理ID | 物理名 | 説明 |
|---------|--------|--------|------|
| User Pool | McpUserPool | `{projectName}-user-pool` | Cognito User Pool |
| User Pool Domain | McpUserPoolDomain | `{projectName}-{accountId}` | トークンエンドポイント用 |
| Resource Server | McpResourceServer | `{projectName}-api` | スコープ定義 |
| App Client | McpAppClient | `{projectName}-app-client` | Client Credentials 用 |
| Cognito Authorizer | McpCognitoAuthorizer | `{projectName}-cognito-authorizer` | API Gateway 用 |

## Lambda Function

### 基本設定

| 設定 | 値 |
|------|-----|
| 関数名 | `{projectName}-mcp` |
| ランタイム | Python 3.12 |
| ハンドラー | `index.handler` |
| アーキテクチャ | x86_64 |
| タイムアウト | 600 秒 (10 分) |
| メモリ | 256 MB |

### トレーシング

| 設定 | 値 |
|------|-----|
| X-Ray | Active |

### 実行ロール

CDK が自動生成する IAM ロール。以下のポリシーが付与されます：

- AWSLambdaBasicExecutionRole（CloudWatch Logs へのログ出力）
- X-Ray 書き込み権限

## API Gateway (REST API)

### 基本設定

| 設定 | 値 |
|------|-----|
| API 名 | `{projectName}-api` |
| タイプ | REST API |
| ステージ | `prd` |
| トレーシング | 有効 |

### エンドポイント

| パス | メソッド | 認証 | 統合 |
|------|---------|------|------|
| `/mcp` | POST | API Key / Cognito | Lambda Proxy |
| `/mcp` | GET | API Key / Cognito | Lambda Proxy |
| `/mcp` | OPTIONS | なし | Mock (CORS) |

### CORS 設定

| 設定 | 値 |
|------|-----|
| Allow Origins | `*` |
| Allow Methods | `*` |
| Allow Headers | Content-Type, x-api-key, Authorization |

## API Key

### 基本設定

| 設定 | 値 |
|------|-----|
| キー名 | `{projectName}-api-key` |
| 有効 | true |

### 取得コマンド

```bash
aws apigateway get-api-key \
  --api-key {ApiKeyId} \
  --include-value \
  --query 'value' \
  --output text
```

## Usage Plan

### 基本設定

| 設定 | 値 |
|------|-----|
| プラン名 | `{projectName}-usage-plan` |
| Rate Limit | 100 requests/sec |
| Burst Limit | 200 requests |

### 関連付け

- API Gateway ステージ: `{projectName}-api` / `prd`
- API Key: `{projectName}-api-key`

## Cognito User Pool

### 基本設定

| 設定 | 値 |
|------|-----|
| プール名 | `{projectName}-user-pool` |
| セルフサインアップ | 無効 |
| サインインエイリアス | Email |
| 削除ポリシー | DESTROY |

## Cognito Domain

### 基本設定

| 設定 | 値 |
|------|-----|
| ドメインプレフィックス | `{projectName}-{accountId}` |

### エンドポイント

```
https://{domainPrefix}.auth.{region}.amazoncognito.com
```

### トークンエンドポイント

```
https://{domainPrefix}.auth.{region}.amazoncognito.com/oauth2/token
```

## Resource Server

### 基本設定

| 設定 | 値 |
|------|-----|
| 識別子 | `{projectName}-api` |
| 名前 | `{projectName}-resource-server` |

### スコープ

| スコープ名 | 説明 |
|-----------|------|
| `mcp.invoke` | MCP ツールの実行権限 |

### 完全スコープ識別子

```
{projectName}-api/mcp.invoke
```

## App Client

### 基本設定

| 設定 | 値 |
|------|-----|
| クライアント名 | `{projectName}-app-client` |
| シークレット生成 | 有効 |
| OAuth フロー | Client Credentials |
| トークン有効期限 | 1 時間 |
| Token Revocation | 有効 |

### Client Secret 取得コマンド

```bash
aws cognito-idp describe-user-pool-client \
  --user-pool-id {UserPoolId} \
  --client-id {AppClientId} \
  --query 'UserPoolClient.ClientSecret' \
  --output text
```

## Cognito Authorizer

### 基本設定

| 設定 | 値 |
|------|-----|
| Authorizer 名 | `{projectName}-cognito-authorizer` |
| Identity Source | `method.request.header.Authorization` |
| User Pools | `{projectName}-user-pool` |

## CloudFormation 出力

### 共通出力

| 出力名 | 説明 | 例 |
|-------|------|-----|
| `McpFunctionArn` | Lambda 関数の ARN | `arn:aws:lambda:ap-northeast-1:123456789012:function:mcp-server-sample-mcp` |
| `McpApiUrl` | API Gateway のベース URL | `https://xxxxxxxxxx.execute-api.ap-northeast-1.amazonaws.com/prd/` |
| `McpApiEndpoint` | MCP エンドポイント URL | `https://xxxxxxxxxx.execute-api.ap-northeast-1.amazonaws.com/prd/mcp` |
| `AuthType` | 認証タイプ | `api-key` または `oauth` |

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
| `TokenEndpoint` | OAuth 2.0 Token Endpoint URL |
| `OAuthScope` | 使用するスコープ |
| `GetClientSecretCommand` | Client Secret 取得コマンド |

## コスト見積もり

### 従量課金コンポーネント

| サービス | 課金単位 |
|---------|---------|
| Lambda | リクエスト数、実行時間 |
| API Gateway | リクエスト数 |
| Cognito | MAU (Monthly Active Users) |
| CloudWatch Logs | ログ量 |

### 無料枠

| サービス | 無料枠 |
|---------|--------|
| Lambda | 100 万リクエスト/月、40 万 GB 秒/月 |
| API Gateway | 100 万リクエスト/月（12ヶ月間） |
| Cognito | 50,000 MAU/月 |

**注意:** 実際のコストは使用量によって異なります。AWS Pricing Calculator で見積もりを行ってください。
