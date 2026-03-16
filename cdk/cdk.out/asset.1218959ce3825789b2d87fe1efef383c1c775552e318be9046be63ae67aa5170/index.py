"""
MCP Lambda Server - service-operations-mcp

MCP Server sample implementation using awslabs.mcp_lambda_handler.
Supports Streamable HTTP transport.
"""

import json
from typing import Any

from awslabs.mcp_lambda_handler import MCPLambdaHandler


# MCPサーバーを初期化
mcp = MCPLambdaHandler(
    name="service-operations-mcp",
    version="1.0.0",
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
                "id": "maintenance-001",
                "start": "2025-04-01T00:00:00+0900",
                "end": "2025-04-01T02:00:00+0900",
                "title": "SSL Certificate Renewal",
                "description": "Renewing SSL certificates. HTTPS connections may be temporarily interrupted.",
                "status": "scheduled",
            },
            {
                "id": "maintenance-002",
                "start": "2025-04-05T02:00:00+0900",
                "end": "2025-04-05T04:00:00+0900",
                "title": "Security Patch",
                "description": "Applying security patches. System may restart during maintenance.",
                "status": "scheduled",
            },
            {
                "id": "maintenance-003",
                "start": "2025-04-10T09:00:00+0900",
                "end": "2025-04-10T12:00:00+0900",
                "title": "Database Maintenance",
                "description": "Optimizing database and rebuilding indexes. Performance may be degraded.",
                "status": "scheduled",
            },
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
        MCPレスポンス
    """
    print("event:", json.dumps(event))
    return mcp.handle_request(event, context)
