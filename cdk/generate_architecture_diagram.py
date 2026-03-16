"""
AWS MCP Server Architecture Diagram Generator

This script generates an architecture diagram using AWS official icons.
Requires: diagrams library (pip install diagrams)
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import Lambda
from diagrams.aws.network import APIGateway
from diagrams.aws.security import Cognito, IAMRole
from diagrams.aws.ml import Bedrock
from diagrams.custom import Custom
import os

# 図の属性設定
graph_attr = {
    "fontsize": "16",
    "bgcolor": "white",
    "pad": "0.5",
}

# ノードの属性設定
node_attr = {
    "fontsize": "12",
}

# エッジの属性設定
edge_attr = {
    "fontsize": "10",
}

with Diagram(
    "MCP Server Architecture",
    filename="mcp_architecture",
    outformat="png",
    show=False,
    direction="LR",
    graph_attr=graph_attr,
    node_attr=node_attr,
    edge_attr=edge_attr,
):
    # クライアント（カスタムアイコンまたはプレースホルダー）
    # Note: diagramsライブラリには汎用的なクライアントアイコンがないため、
    # 他のAWSサービスで代用するか、カスタムアイコンを使用
    from diagrams.aws.engagement import SimpleEmailServiceSes
    client = SimpleEmailServiceSes("DevOps Agent\n/ Client")

    with Cluster("Authentication & Authorization"):
        cognito_pool = Cognito("Cognito User Pool\n(cmn-genai-mcp-server-sample-dev-user-pool)")
        cognito_client = Cognito("User Pool Client\n(OAuth Client Credentials)")
        cognito_domain = Cognito("User Pool Domain\n(cmn-genai-mcp-server-sample-dev)")

        # Cognitoの内部関係
        cognito_pool - Edge(style="dotted") - cognito_domain
        cognito_domain - Edge(style="dotted") - cognito_client

    with Cluster("Bedrock AgentCore"):
        gateway = Bedrock("AgentCore Gateway\n(MCP Protocol)\n(CUSTOM_JWT Auth)")
        gateway_role = IAMRole("Gateway Role\n(execute-api:Invoke)")

        gateway - Edge(style="dotted", label="AssumeRole") - gateway_role

    with Cluster("API Gateway"):
        api_gateway = APIGateway("REST API\n(cmn-genai-mcp-server-sample-dev-api)")
        api_method = APIGateway("/mcp\n(GET Method)\n(AWS_IAM Auth)\n(Response Streaming)")

        api_gateway >> api_method

    with Cluster("Compute"):
        lambda_func = Lambda("Lambda Function\n(cmn-genai-mcp-server-sample-dev-mcp)\n(Node.js 22)\n(Response Streaming)")

    # 認証フロー
    client >> Edge(label="1. OAuth 2.0\nClient Credentials") >> cognito_domain
    cognito_domain >> Edge(label="2. Access Token", style="dashed", color="green") >> client

    # リクエストフロー
    client >> Edge(label="3. JWT Token\n+ MCP Request") >> gateway
    gateway >> Edge(label="4. Token\nValidation", style="dotted") >> cognito_pool
    gateway >> Edge(label="5. AWS IAM Auth\n(via Gateway Role)") >> api_gateway
    api_gateway >> Edge(label="6. Invoke With\nResponse Stream") >> lambda_func

    # レスポンスフロー（ストリーミング）
    lambda_func >> Edge(label="7-10. Streaming\nResponse", style="bold", color="blue") >> api_method
    api_method >> Edge(label="", style="bold", color="blue") >> gateway
    gateway >> Edge(label="", style="bold", color="blue") >> client

print("Architecture diagram generated: mcp_architecture.png")
