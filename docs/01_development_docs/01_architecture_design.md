# アーキテクチャ設計

## 概要

本プロジェクトは、AWS Lambda 上で動作する MCP Server のサーバーレスアーキテクチャを採用しています。API Gateway を通じてリクエストを受け付け、Lambda 関数で MCP プロトコルを処理します。

## アーキテクチャ図

### API Key 認証

![API Key 認証アーキテクチャ](../../assets/architecture-api-key.png)

### OAuth 2.0 認証

![OAuth 認証アーキテクチャ](../../assets/architecture-oauth.png)

## システム構成

### コンポーネント概要

```mermaid
graph TB
    subgraph "クライアント"
        Client[MCP Client]
    end

    subgraph "API Gateway"
        RestAPI[REST API<br/>{projectName}-api]
        ApiKey[API Key<br/>{projectName}-api-key]
        UsagePlan[Usage Plan<br/>rate: 100, burst: 200]
        McpResource[Resource: /mcp]
        McpMethodPost[Method: POST<br/>Auth: API Key]
        McpMethodGet[Method: GET<br/>Auth: API Key]
    end

    subgraph "Lambda"
        McpFunction[Lambda Function<br/>{projectName}-mcp<br/>Runtime: Python 3.12<br/>Handler: awslabs.mcp_lambda_handler]
    end

    subgraph "MCP Server"
        MCPHandler[MCPLambdaHandler<br/>name: service-operations-mcp]
        Tool1[Tool: get_schedule]
    end

    Client -->|1. x-api-key header| RestAPI
    ApiKey -.->|認証| RestAPI
    UsagePlan -.->|スロットリング| RestAPI
    RestAPI --> McpResource
    McpResource --> McpMethodPost
    McpResource --> McpMethodGet
    McpMethodPost -->|2. JSON-RPC Request| McpFunction
    McpMethodGet -->|2. JSON-RPC Request| McpFunction
    McpFunction --> MCPHandler
    MCPHandler --> Tool1
    Tool1 -->|3. JSON Response| MCPHandler
    MCPHandler -->|4. JSON-RPC Response| McpFunction
    McpFunction -->|5. Response| RestAPI
    RestAPI -->|6. Response| Client
```

## 通信フロー

### MCP リクエストフロー

1. クライアントが認証ヘッダー付きで API Gateway にリクエスト
   - API Key 認証: `x-api-key` ヘッダー
   - OAuth 認証: `Authorization: Bearer <token>` ヘッダー
2. API Gateway が認証を検証
3. API Gateway が Lambda 関数を呼び出し（Lambda Proxy 統合）
4. Lambda 関数内の `MCPLambdaHandler` が JSON-RPC リクエストを処理
5. 該当ツール（`get_schedule`）を実行
6. JSON-RPC レスポンスを返却

### サポートする MCP メソッド

| メソッド | 説明 |
|---------|------|
| `initialize` | クライアント接続の初期化 |
| `tools/list` | 利用可能なツール一覧を取得 |
| `tools/call` | ツールを実行 |
| `ping` | ヘルスチェック |

## レイヤー構成

### プレゼンテーション層

- **API Gateway REST API**
  - `/mcp` エンドポイント（POST, GET）
  - CORS 設定（全オリジン許可）
  - ステージ: `prd`

### ビジネスロジック層

- **Lambda 関数**
  - MCP プロトコル処理
  - ツール実行
  - JSON-RPC レスポンス生成

### 認証層

- **API Key 認証モード**
  - API Key
  - Usage Plan（レート制限）

- **OAuth 認証モード**
  - Cognito User Pool
  - Cognito Authorizer
  - Resource Server

## 設計原則

### サーバーレス

- Lambda によるオンデマンド実行
- スケールアウト自動対応
- 従量課金制

### Infrastructure as Code

- AWS CDK による全リソースの定義
- TypeScript による型安全な構成
- 環境差分の最小化

### セキュリティ

- 認証必須（API Key または OAuth）
- HTTPS 通信
- X-Ray トレーシング有効

## 非機能要件

### パフォーマンス

| 項目 | 値 |
|------|-----|
| Lambda タイムアウト | 600 秒 (10 分) |
| Lambda メモリ | 256 MB |
| API Gateway スロットリング (API Key) | Rate: 100 req/sec, Burst: 200 |

### 可用性

- Lambda のマルチ AZ 自動配置
- API Gateway の高可用性
- Cognito のリージョン内冗長性

### 監視

- CloudWatch Logs によるログ収集
- X-Ray によるトレーシング
- API Gateway のメトリクス

## 制約事項

- VPC 内ホストは未サポート（VPC内ホストは、DevOps Agentで未サポート）
- ステートレス設計（セッション永続化はオプション）
- Lambda のコールドスタート遅延あり
