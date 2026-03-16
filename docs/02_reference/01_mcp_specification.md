# MCP 仕様準拠

## 概要

MCP (Model Context Protocol) は、LLM アプリケーションとツール/リソースを接続するためのオープンプロトコルです。本プロジェクトは MCP 仕様に準拠した Server 実装を提供します。

## AWS DevOps Agent 対応

本プロジェクトは、**AWS DevOps Agent** から使用するための MCP サーバーとして設計されています。

以下の AWS ドキュメントに基づき、必要な仕様を満たす実装となっています：

- [Configuring capabilities for AWS DevOps Agent: Connecting MCP servers](https://docs.aws.amazon.com/devopsagent/latest/userguide/configuring-capabilities-for-aws-devops-agent-connecting-mcp-servers.html)

### AWS DevOps Agent の MCP Server 要件

AWS DevOps Agent が MCP Server に接続するための要件：

| 要件 | 本プロジェクトでの対応 |
|------|----------------------|
| Streamable HTTP トランスポート | ✅ awslabs.mcp_lambda_handler で対応 |
| API キー/トークンベースの認証 | ✅ API Key 認証対応 |
| OAuth 2.0 認証 | ✅ Cognito Client Credentials Flow 対応 |
| VPC 内ホスト未サポート | ✅ VPC 設定なし (パブリックエンドポイント) |

## MCP 仕様への適合状況

| 仕様 | 対応状況 | 備考 |
|------|:--------:|------|
| Streamable HTTP | ✅ | awslabs.mcp_lambda_handler で対応 |
| JSON-RPC 2.0 | ✅ | 標準準拠 |
| API キー/トークンベースの認証 | ✅ | API Key 認証対応 |
| OAuth 2.0 認証 | ✅ | Client Credentials Flow 対応 |
| VPC 内ホスト未サポート | ✅ | VPC 設定なし |
| ツール (Tools) | ✅ | @mcp.tool() デコレータで定義 |
| リソース (Resources) | ❌ | 未実装 |
| プロンプト (Prompts) | ❌ | 未実装 |

## サポートする MCP メソッド

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
        "text": "{\"schedules\": [...], ...}"
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

## トランスポートプロトコル

### Streamable HTTP

本プロジェクトは Streamable HTTP トランスポートを使用します。

| 項目 | 値 |
|------|-----|
| プロトコル | HTTPS |
| メソッド | POST, GET |
| Content-Type | application/json |

### エンドポイント

```
POST /mcp
GET /mcp
```

## 認証

### AWS DevOps Agent 対応

AWS DevOps Agent の MCP Server 接続要件に準拠しています。

| 要件 | 対応状況 |
|------|:--------:|
| Streamable HTTP | ✅ |
| API キー/トークンベースの認証 | ✅ |
| OAuth 2.0 | ✅ |
| VPC 内ホスト未サポート | ✅ |

## awslabs.mcp_lambda_handler

### 概要

AWS Labs が提供する Python ライブラリで、AWS Lambda 上で MCP サーバーを構築するためのフレームワークです。

### 機能

| 機能 | 説明 |
|------|------|
| Streamable HTTP | MCP 仕様の Streamable HTTP トランスポートをサポート |
| ツール定義 | `@mcp.tool()` デコレータで簡単にツールを定義 |
| セッション管理 | DynamoDB を使用したセッション状態の永続化（オプション） |
| 型検証 | 関数の引数・戻り値の型を自動検証 |

### 使用例

```python
from awslabs.mcp_lambda_handler import MCPLambdaHandler

mcp = MCPLambdaHandler(
    name="my-mcp-server",
    version="1.0.0",
)

@mcp.tool()
def my_tool(param1: str, param2: int = 10) -> str:
    """ツールの説明"""
    return f"Result: {param1}, {param2}"

def handler(event, context):
    return mcp.handle_request(event, context)
```

## 関連リンク

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [AWS DevOps Agent - MCP Server Configuration](https://docs.aws.amazon.com/devopsagent/latest/userguide/configuring-capabilities-for-aws-devops-agent-connecting-mcp-servers.html)
- [awslabs/mcp](https://github.com/awslabs/mcp)
- [awslabs.mcp-lambda-handler (PyPI)](https://pypi.org/project/awslabs.mcp-lambda-handler/)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector)

## MCP Inspector での確認

```bash
npx @modelcontextprotocol/inspector \
  --transport streamable-http \
  --url "{McpApiEndpoint}" \
  --header "x-api-key: {API_KEY}"
```

MCP Inspector を使用すると、以下の確認が可能です：

- サーバー情報の確認
- 利用可能なツール一覧
- ツールの実行テスト
- リクエスト/レスポンスの確認
