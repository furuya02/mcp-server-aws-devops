"""
MCP Lambda Server - service-operations-mcp

AWS DevOps Agent と連携する MCP サーバー。
awslabs.mcp_lambda_handler を使用して Streamable HTTP をサポート。
"""

import json
from typing import Any

from awslabs.mcp_lambda_handler import MCPLambdaHandler


# MCPサーバーを初期化
mcp = MCPLambdaHandler(
    name="service-operations-mcp",
    version="1.0.0",
    instructions="サービス運用に関する情報を提供するMCPサーバーです。",
)


@mcp.tool()
def get_schedule() -> str:
    """
    サービス運用のスケジュールを取得します。

    Returns:
        JSON形式のスケジュール情報
    """
    schedule_data = {
        "schedules": [
            {
                "account": "637423290077",
                "start": "2026-03-01T00:00:00+0900",
                "end": "2026-03-01T02:00:00+0900",
                "title": "SSL証明書更新",
                "description": "EX1およびEX2のSSL証明書を更新します。更新中は一時的にHTTPS接続が切断されます。",
            },
            {
                "account": "637423290077",
                "start": "2026-03-02T02:00:00+0900",
                "end": "2026-03-02T04:00:00+0900",
                "title": "セキュリティパッチ適用",
                "description": "EX2のサーバにセキュリティパッチを適用します。作業中はシステムが再起動される場合があります。",
            },
            {
                "account": "637423290077",
                "start": "2026-03-05T09:00:00+0900",
                "end": "2026-03-05T12:00:00+0900",
                "title": "データベースメンテナンス",
                "description": "本番データベースの最適化とインデックス再構築を行います。パフォーマンスが低下する可能性があります。",
            },
            {
                "account": "637423290077",
                "start": "2026-03-11T22:00:00+0900",
                "end": "2026-03-12T06:00:00+0900",
                "title": "ネットワーク機器更新",
                "description": "データセンターのネットワーク機器を更新します。断続的な接続障害が発生する可能性があります。",
            },
            {
                "account": "9820-8108-8599",
                "start": "2026-03-12T10:00:00+0900",
                "end": "2026-03-12T15:00:00+0900",
                "title": "定期メンテナンス",
                "description": "EX1のサーバの定期メンテナンスが実施されます。130.3.11.1, 130.3.11.2, 130.3.11.3, 130.3.11.6, 130.3.11.7, 130.3.11.8, 130.3.11.10, のサーバに、一時的にアクセス出来ないことがあります。",
            },
        ],
        "timezone": "Asia/Tokyo",
        "last_updated": "2026-03-15T00:00:00+09:00",
    }

    return json.dumps(schedule_data, ensure_ascii=False, indent=2)


def handler(event: Any, context: Any) -> dict[str, Any]:
    """
    Lambda ハンドラー関数。

    Args:
        event: Lambda イベントオブジェクト
        context: Lambda コンテキストオブジェクト

    Returns:
        MCPレスポンス
    """
    print("event:", json.dumps(event))
    return mcp.handle_request(event, context)
