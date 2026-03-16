# API 設計

## 概要

本プロジェクトは MCP (Model Context Protocol) に準拠した API を提供します。API Gateway REST API を通じて、JSON-RPC 2.0 形式のリクエストを処理します。

## エンドポイント

### ベース URL

```
https://{api-id}.execute-api.{region}.amazonaws.com/prd
```

### MCP エンドポイント

| メソッド | パス | 説明 |
|---------|------|------|
| POST | `/mcp` | MCP リクエストを処理 |
| GET | `/mcp` | MCP リクエストを処理（SSE 対応） |

## リクエスト形式

### ヘッダー

#### API Key 認証

```http
POST /mcp HTTP/1.1
Host: {api-id}.execute-api.{region}.amazonaws.com
x-api-key: {API_KEY}
Content-Type: application/json
```

#### OAuth 認証

```http
POST /mcp HTTP/1.1
Host: {api-id}.execute-api.{region}.amazonaws.com
Authorization: Bearer {ACCESS_TOKEN}
Content-Type: application/json
```

### ボディ (JSON-RPC 2.0)

```json
{
  "jsonrpc": "2.0",
  "method": "method_name",
  "params": { ... },
  "id": 1
}
```

## サポートするメソッド

### initialize

クライアント接続を初期化します。

**リクエスト:**
```json
{
  "jsonrpc": "2.0",
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {
      "name": "example-client",
      "version": "1.0.0"
    }
  },
  "id": 1
}
```

**レスポンス:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {}
    },
    "serverInfo": {
      "name": "service-operations-mcp",
      "version": "1.0.0"
    }
  }
}
```

### tools/list

利用可能なツール一覧を取得します。

**リクエスト:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "id": 1
}
```

**レスポンス:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "get_schedule",
        "description": "サービス運用のスケジュールを取得します。",
        "inputSchema": {
          "type": "object",
          "properties": {},
          "required": []
        }
      }
    ]
  }
}
```

### tools/call

指定されたツールを実行します。

**リクエスト:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "get_schedule",
    "arguments": {}
  },
  "id": 2
}
```

**レスポンス:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"schedules\": [...], \"timezone\": \"Asia/Tokyo\", ...}"
      }
    ]
  }
}
```

### ping

ヘルスチェック用のメソッドです。

**リクエスト:**
```json
{
  "jsonrpc": "2.0",
  "method": "ping",
  "id": 1
}
```

**レスポンス:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {}
}
```

## 提供ツール

### get_schedule

サービス運用のスケジュールを取得します。

| 項目 | 値 |
|------|-----|
| ツール名 | `get_schedule` |
| 説明 | サービス運用のスケジュールを取得します |
| 引数 | なし |
| 戻り値 | JSON 形式のスケジュール情報 |

**レスポンス構造:**

```json
{
  "schedules": [
    {
      "id": "maintenance-001",
      "start": "2025-04-01T00:00:00+0900",
      "end": "2025-04-01T02:00:00+0900",
      "title": "SSL Certificate Renewal",
      "description": "Renewing SSL certificates. HTTPS connections may be temporarily interrupted.",
      "status": "scheduled"
    }
  ],
  "timezone": "Asia/Tokyo",
  "last_updated": "2025-03-15T00:00:00+09:00"
}
```

**スケジュール項目:**

| フィールド | 型 | 説明 |
|-----------|------|------|
| `id` | string | スケジュール ID |
| `start` | string | 開始日時 (ISO 8601) |
| `end` | string | 終了日時 (ISO 8601) |
| `title` | string | タイトル |
| `description` | string | 説明 |
| `status` | string | ステータス |

## エラーレスポンス

### JSON-RPC エラー

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32600,
    "message": "Invalid Request"
  }
}
```

**標準エラーコード:**

| コード | メッセージ | 説明 |
|--------|----------|------|
| -32700 | Parse error | JSON パースエラー |
| -32600 | Invalid Request | 無効なリクエスト |
| -32601 | Method not found | メソッドが見つからない |
| -32602 | Invalid params | 無効なパラメータ |
| -32603 | Internal error | 内部エラー |

### HTTP エラー

| ステータスコード | 説明 |
|----------------|------|
| 400 | Bad Request |
| 401 | Unauthorized（認証失敗） |
| 403 | Forbidden（認可失敗） |
| 429 | Too Many Requests（レート制限） |
| 500 | Internal Server Error |

## CORS 設定

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type, x-api-key, Authorization
```

## レート制限

API Key 認証時の Usage Plan 設定：

| 設定 | 値 |
|------|-----|
| Rate Limit | 100 requests/sec |
| Burst Limit | 200 requests |

## 動作確認

### curl を使用した確認

#### tools/list の呼び出し (API Key)

```bash
curl -X POST "https://{api-id}.execute-api.ap-northeast-1.amazonaws.com/prd/mcp" \
  -H "x-api-key: {API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }'
```

#### get_schedule ツールの呼び出し (API Key)

```bash
curl -X POST "https://{api-id}.execute-api.ap-northeast-1.amazonaws.com/prd/mcp" \
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

### MCP Inspector を使用した確認

```bash
npx @modelcontextprotocol/inspector \
  --transport streamable-http \
  --url "https://{api-id}.execute-api.ap-northeast-1.amazonaws.com/prd/mcp" \
  --header "x-api-key: {API_KEY}"
```
