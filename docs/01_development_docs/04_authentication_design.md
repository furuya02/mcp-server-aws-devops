# 認証設計

## 概要

本プロジェクトは2種類の認証方式をサポートしています。デプロイ時にどちらかを選択して使用します。

| 認証タイプ | 説明 | ユースケース |
|----------|------|-------------|
| `api-key` | API Key 認証（デフォルト） | シンプルな認証が必要な場合 |
| `oauth` | OAuth 2.0 (Client Credentials) | 標準的な認証フローが必要な場合 |

## API Key 認証

### 概要

API Gateway の API Key 機能を使用したシンプルな認証方式です。

### アーキテクチャ

```
Client --> [x-api-key header] --> API Gateway --> Lambda
                                      |
                                  API Key 検証
                                      |
                                  Usage Plan
                                  (Rate Limit)
```

### 作成されるリソース

| リソース | 名前 | 説明 |
|---------|------|------|
| API Key | `{projectName}-api-key` | API キー |
| Usage Plan | `{projectName}-usage-plan` | スロットリング設定 |

### Usage Plan 設定

| 設定 | 値 |
|------|-----|
| Rate Limit | 100 requests/sec |
| Burst Limit | 200 requests |

### API Key の取得方法

デプロイ後、以下のコマンドで API Key 値を取得します：

```bash
aws apigateway get-api-key \
  --api-key {ApiKeyId} \
  --include-value \
  --query 'value' \
  --output text
```

### リクエスト方法

```bash
curl -X POST "{McpApiEndpoint}" \
  -H "x-api-key: {API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }'
```

## OAuth 2.0 認証

### 概要

Amazon Cognito を使用した OAuth 2.0 Client Credentials Flow による認証方式です。

### アーキテクチャ

```
                                    Token Endpoint
                                         |
                                         v
Client --> [client_credentials] --> Cognito --> Access Token
   |
   |  [Authorization: Bearer token]
   v
API Gateway --> Cognito Authorizer --> Lambda
```

### 作成されるリソース

| リソース | 名前 | 説明 |
|---------|------|------|
| User Pool | `{projectName}-user-pool` | Cognito User Pool |
| Domain | `{projectName}-{accountId}` | トークンエンドポイント用ドメイン |
| Resource Server | `{projectName}-api` | スコープ定義 |
| App Client | `{projectName}-app-client` | Client Credentials 用 |
| Authorizer | `{projectName}-cognito-authorizer` | API Gateway 用 |

### スコープ

| スコープ | 説明 |
|---------|------|
| `{projectName}-api/mcp.invoke` | MCP ツールの実行権限 |

### Client Credentials Flow

#### 1. Client Secret の取得

```bash
aws cognito-idp describe-user-pool-client \
  --user-pool-id {UserPoolId} \
  --client-id {AppClientId} \
  --query 'UserPoolClient.ClientSecret' \
  --output text
```

#### 2. アクセストークンの取得

```bash
curl -X POST "{TokenEndpoint}" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -u "{AppClientId}:{ClientSecret}" \
  -d "grant_type=client_credentials&scope={OAuthScope}"
```

**レスポンス例:**

```json
{
  "access_token": "eyJraWQiOi...",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

#### 3. API の呼び出し

```bash
curl -X POST "{McpApiEndpoint}" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }'
```

### トークン設定

| 設定 | 値 |
|------|-----|
| アクセストークン有効期限 | 1 時間 |
| Token Revocation | 有効 |

### トークン更新

アクセストークンの有効期限が切れた場合は、再度 Client Credentials Flow を実行してトークンを取得します。

## 認証方式の選択

### デプロイ時の指定

#### API Key 認証（デフォルト）

```bash
npx cdk deploy
# または
npx cdk deploy -c authType=api-key
```

#### OAuth 認証

```bash
npx cdk deploy -c authType=oauth
```

### 選択基準

| 要件 | 推奨認証方式 |
|------|-------------|
| シンプルな実装 | API Key |
| 標準的な認証フロー | OAuth |
| 細かいアクセス制御 | OAuth |
| レート制限が必要 | API Key |
| トークンベースの認証 | OAuth |

## セキュリティ考慮事項

### API Key 認証

- API Key はリクエストヘッダーで送信
- Usage Plan によるレート制限
- API Key の定期的なローテーションを推奨

### OAuth 認証

- Client Secret は安全に管理
- アクセストークンは1時間で失効
- HTTPS 通信必須
- スコープによるアクセス制御

### 共通

- 認証情報をコードやログに含めない
- AWS Secrets Manager などで認証情報を管理
- 必要に応じてキー/シークレットをローテーション

## CloudFormation 出力一覧

### API Key 認証時

| 出力名 | 説明 |
|-------|------|
| `ApiKeyId` | API Key ID |
| `GetApiKeyCommand` | API Key 値取得コマンド |

### OAuth 認証時

| 出力名 | 説明 |
|-------|------|
| `UserPoolId` | Cognito User Pool ID |
| `AppClientId` | Cognito App Client ID |
| `TokenEndpoint` | OAuth 2.0 Token Endpoint URL |
| `OAuthScope` | 使用するスコープ |
| `GetClientSecretCommand` | Client Secret 取得コマンド |
