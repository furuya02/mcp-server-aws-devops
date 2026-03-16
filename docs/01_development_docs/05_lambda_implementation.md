# Lambda 実装

## 概要

本プロジェクトの Lambda 関数は Python 3.12 で実装されており、`awslabs.mcp_lambda_handler` ライブラリを使用して MCP Server を構築しています。

### サンプル実装について

本プロジェクトはサンプル実装のため、**最小限の Tool のみ**を提供しています。

| ツール名 | 説明 |
|---------|------|
| `get_schedule` | サービス運用のスケジュールを取得 |

実際のプロジェクトでは、以下の「ツールの追加方法」を参考に Tool を追加して拡張してください。

## ファイル構成

```
cdk/lambda_python/
├── index.py            # メイン Lambda 関数
└── requirements.txt    # Python 依存関係
```

## 依存関係

### requirements.txt

```
awslabs.mcp-lambda-handler>=0.1.14
```

## awslabs.mcp_lambda_handler について

AWS Labs が提供する Python ライブラリで、AWS Lambda 上で MCP サーバーを構築するためのフレームワークです。

### リソース

- **PyPI**: [awslabs.mcp-lambda-handler](https://pypi.org/project/awslabs.mcp-lambda-handler/)
- **GitHub**: [awslabs/mcp](https://github.com/awslabs/mcp)

### 主な機能

| 機能 | 説明 |
|------|------|
| Streamable HTTP | MCP 仕様の Streamable HTTP トランスポートをサポート |
| ツール定義 | `@mcp.tool()` デコレータで簡単にツールを定義 |
| セッション管理 | DynamoDB を使用したセッション状態の永続化（オプション） |
| 型検証 | 関数の引数・戻り値の型を自動検証 |

## 実装詳細

### index.py

```python
"""
MCP Lambda Server - service-operations-mcp

MCP Server sample implementation using awslabs.mcp_lambda_handler.
Supports Streamable HTTP transport.
"""

import json
from typing import Any

from awslabs.mcp_lambda_handler import MCPLambdaHandler


# MCP サーバーを初期化
mcp = MCPLambdaHandler(
    name="service-operations-mcp",
    version="1.0.0",
)


@mcp.tool()
def get_schedule() -> str:
    """
    サービス運用のスケジュールを取得します。

    Returns:
        JSON 形式のスケジュール情報
    """
    schedule_data = {
        "schedules": [
            {
                "id": "maintenance-001",
                "start": "2025-04-01T00:00:00+0900",
                "end": "2025-04-01T02:00:00+0900",
                "title": "SSL Certificate Renewal",
                "description": "Renewing SSL certificates...",
                "status": "scheduled",
            },
            # ... 他のスケジュール
        ],
        "timezone": "Asia/Tokyo",
        "last_updated": "2025-03-15T00:00:00+09:00",
    }

    return json.dumps(schedule_data, ensure_ascii=False, indent=2)


def handler(event: Any, context: Any) -> dict[str, Any]:
    """
    Lambda ハンドラー関数。

    Args:
        event: Lambda イベントオブジェクト
        context: Lambda コンテキストオブジェクト

    Returns:
        MCP レスポンス
    """
    print("event:", json.dumps(event))
    return mcp.handle_request(event, context)
```

## コンポーネント説明

### MCPLambdaHandler

MCP サーバーのメインクラスです。

```python
mcp = MCPLambdaHandler(
    name="service-operations-mcp",  # サーバー名
    version="1.0.0",                # バージョン
)
```

| パラメータ | 型 | 説明 |
|-----------|------|------|
| `name` | str | サーバー名（クライアントに返される） |
| `version` | str | サーバーバージョン |

### @mcp.tool() デコレータ

ツールを定義するためのデコレータです。

```python
@mcp.tool()
def my_tool(param1: str, param2: int = 10) -> str:
    """ツールの説明（docstring がツールの説明として使用される）"""
    return f"Result: {param1}, {param2}"
```

**特徴:**
- 関数の docstring がツールの説明として使用される
- 引数の型アノテーションから入力スキーマが自動生成される
- デフォルト値を持つ引数はオプションパラメータとなる

### handler 関数

Lambda のエントリーポイントです。

```python
def handler(event: Any, context: Any) -> dict[str, Any]:
    print("event:", json.dumps(event))
    return mcp.handle_request(event, context)
```

## ツールの追加方法

### 基本的なツール

```python
@mcp.tool()
def simple_tool() -> str:
    """シンプルなツール"""
    return "Hello, World!"
```

### パラメータ付きツール

```python
@mcp.tool()
def greet(name: str, greeting: str = "Hello") -> str:
    """
    挨拶を返します。

    Args:
        name: 名前
        greeting: 挨拶文（デフォルト: Hello）
    """
    return f"{greeting}, {name}!"
```

### 複雑な戻り値

```python
@mcp.tool()
def get_data() -> str:
    """データを取得します"""
    data = {
        "items": [1, 2, 3],
        "count": 3,
    }
    return json.dumps(data, ensure_ascii=False)
```

## サポートする MCP メソッド

| メソッド | 説明 |
|---------|------|
| `initialize` | クライアント接続の初期化 |
| `tools/list` | 登録されたツール一覧を返す |
| `tools/call` | 指定されたツールを実行 |
| `ping` | ヘルスチェック |

## Lambda 設定

### CDK での設定

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

### 設定値

| 設定 | 値 | 説明 |
|------|-----|------|
| ランタイム | Python 3.12 | 実行環境 |
| ハンドラー | `index.handler` | エントリーポイント |
| アーキテクチャ | x86_64 | CPU アーキテクチャ |
| タイムアウト | 600 秒 | 最大実行時間 |
| メモリ | 256 MB | 割り当てメモリ |
| トレーシング | Active | X-Ray 有効 |

## バンドリング

Docker を使用して Python 依存関係をバンドルします。

```bash
pip install -r requirements.txt -t /asset-output && cp -r . /asset-output
```

**注意:** デプロイ時に Docker が必要です。

## ログ出力

Lambda 関数内のログは CloudWatch Logs に出力されます。

```python
print("event:", json.dumps(event))
```

ログストリーム: `/aws/lambda/{projectName}-mcp`

## トラブルシューティング

### デプロイエラー

**Docker が起動していない場合:**
```
Error: Cannot connect to the Docker daemon
```
→ Docker Desktop を起動してください。

### ランタイムエラー

**モジュールが見つからない場合:**
```
ModuleNotFoundError: No module named 'awslabs'
```
→ `requirements.txt` の依存関係を確認してください。

### タイムアウト

長時間実行されるツールがある場合は、タイムアウト設定を調整してください。

```typescript
timeout: cdk.Duration.seconds(900),  // 15分に延長
```
