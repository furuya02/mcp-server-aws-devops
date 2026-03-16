# MCP Server Architecture

## サーバー情報

| 項目 | 値 |
|------|-----|
| サーバー名 | `service-operations-mcp` |
| バージョン | `1.0.0` |
| プロトコル | Streamable HTTP |
| ライブラリ | `awslabs.mcp_lambda_handler` |

## 提供ツール

| ツール名 | 説明 | 引数 | 戻り値 |
|---------|------|------|--------|
| `get_schedule` | サービス運用のスケジュールを取得 | なし | JSON |

## リソース構成図

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

    %% リクエストフロー
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

    %% スタイル定義
    classDef api fill:#FF4F8B,stroke:#232F3E,stroke-width:2px,color:#fff
    classDef lambda fill:#FF9900,stroke:#232F3E,stroke-width:2px,color:#fff
    classDef client fill:#232F3E,stroke:#FF9900,stroke-width:2px,color:#fff
    classDef auth fill:#DD344C,stroke:#232F3E,stroke-width:2px,color:#fff
    classDef mcp fill:#7B42BC,stroke:#232F3E,stroke-width:2px,color:#fff

    class RestAPI,McpResource,McpMethodPost,McpMethodGet api
    class McpFunction lambda
    class Client client
    class ApiKey,UsagePlan auth
    class MCPHandler,Tool1 mcp
```

## リソース一覧

### 1. Lambda Function
- **名前**: `{projectName}-mcp`
- **ランタイム**: Python 3.12
- **タイムアウト**: 600秒 (10分)
- **メモリ**: 256 MB
- **トレーシング**: X-Ray Active
- **依存関係**: `awslabs.mcp_lambda_handler`

### 2. API Gateway (REST API)
- **名前**: `{projectName}-api`
- **ステージ**: prd
- **エンドポイント**: `/mcp`
- **メソッド**: POST, GET
- **認証**: API Key
- **統合**: Lambda Proxy

### 3. API Key
- **名前**: `{projectName}-api-key`
- **用途**: MCP クライアントからの認証

### 4. Usage Plan
- **名前**: `{projectName}-usage-plan`
- **Rate Limit**: 100 requests/sec
- **Burst Limit**: 200 requests

## 通信フロー

### MCPリクエストフロー
1. クライアントが `x-api-key` ヘッダー付きで API Gateway にリクエスト
2. API Gateway が API Key を検証
3. API Gateway が Lambda 関数を呼び出し（Lambda Proxy統合）
4. Lambda 関数内の `MCPLambdaHandler` が JSON-RPC リクエストを処理
5. 該当ツール（`get_schedule`）を実行
6. JSON-RPC レスポンスを返却

### サポートするMCPメソッド

| メソッド | 説明 |
|---------|------|
| `initialize` | クライアント接続の初期化 |
| `tools/list` | 利用可能なツール一覧を取得 |
| `tools/call` | ツールを実行 |

## MCP仕様への適合

| 仕様 | 対応状況 |
|------|:--------:|
| Streamable HTTP | ✅ |
| API キー/トークンベースの認証 | ✅ |
| VPC 内ホスト未サポート | ✅ (VPC設定なし) |
| JSON-RPC 2.0 | ✅ |
