# MCP Server CDK

This project builds an MCP server on Lambda for use with **AWS DevOps Agent**. Infrastructure is managed with AWS CDK.

The implementation meets the required specifications based on the following AWS documentation:

- [Configuring capabilities for AWS DevOps Agent: Connecting MCP servers](https://docs.aws.amazon.com/devopsagent/latest/userguide/configuring-capabilities-for-aws-devops-agent-connecting-mcp-servers.html)

### Supported Specifications

| Requirement | Status |
|-------------|:------:|
| Streamable HTTP Transport | ✅ |
| API Key/Token-based Authentication | ✅ (Switchable) |
| OAuth 2.0 Authentication (Client Credentials Flow) | ✅ (Switchable) |
| VPC-hosted Endpoints Not Supported | ✅ (VPC-hosted endpoints are not supported by DevOps Agent) |
| JSON-RPC 2.0 | ✅ |

### About the Sample Implementation

This project is a sample implementation and provides **only minimal tools**.

| Tool Name | Description |
|-----------|-------------|
| `get_schedule` | Get service operations schedule |

For actual projects, extend by adding tools to `cdk/lambda_python/index.py`.

## Architecture

Two authentication methods are supported.

### API Key Authentication (Default)

![](assets/architecture-api-key.png)

### OAuth 2.0 Authentication (Client Credentials Flow)

![](assets/architecture-oauth.png)

## Server Information

| Item | Value |
|------|-------|
| Server Name | `service-operations-mcp` |
| Version | `1.0.0` |
| Protocol | Streamable HTTP |

## Provided Tools

| Tool Name | Description | Arguments | Return Value |
|-----------|-------------|-----------|--------------|
| `get_schedule` | Get service operations schedule | None | JSON |

## Structure

```
mcp-server-aws-devops/
├── assets/
│   ├── architecture-api-key.drawio  # API Key auth architecture diagram
│   └── architecture-oauth.drawio    # OAuth auth architecture diagram
├── cdk/                             # CDK project
└── README.md
```

### CDK Directory

```
cdk/
├── bin/
│   └── cdk.ts              # CDK entry point
├── lib/
│   └── mcp-stack.ts        # Main stack (with auth switching support)
├── lambda_python/
│   ├── index.py            # Lambda function implementation (Python)
│   └── requirements.txt    # Python dependencies
├── cdk.json                # CDK configuration (includes authType setting)
├── package.json            # Dependencies
└── tsconfig.json           # TypeScript configuration
```

## Authentication Methods

### Switching Authentication Type

Switch using `context.authType` in `cdk.json` or the `-c authType=` option during deployment.

| authType | Description | Authentication Method |
|----------|-------------|----------------------|
| `api-key` (Default) | API Key Authentication | `x-api-key` header |
| `oauth` | OAuth 2.0 (Client Credentials) | `Authorization: Bearer <token>` header |

### Resources Created with API Key Authentication

| Resource | Description |
|----------|-------------|
| Lambda Function | MCP Server (Python 3.12) |
| API Gateway | REST API (API Key Authentication) |
| API Key | For API Key authentication |
| Usage Plan | Throttling settings (rate: 100, burst: 200) |

### Resources Created with OAuth Authentication

| Resource | Description |
|----------|-------------|
| Lambda Function | MCP Server (Python 3.12) |
| API Gateway | REST API (Cognito Authorizer) |
| Cognito User Pool | OAuth 2.0 IdP |
| Cognito Domain | For token endpoint |
| Resource Server | Scope definition (`mcp.invoke`) |
| App Client | For Client Credentials Flow |

## About awslabs.mcp_lambda_handler

`awslabs.mcp_lambda_handler` is a Python library provided by AWS Labs, a framework for building MCP servers on AWS Lambda.

- **PyPI**: [awslabs.mcp-lambda-handler](https://pypi.org/project/awslabs.mcp-lambda-handler/)
- **GitHub**: [awslabs/mcp](https://github.com/awslabs/mcp)

### Key Features

| Feature | Description |
|---------|-------------|
| Streamable HTTP | Supports MCP specification Streamable HTTP transport |
| Tool Definition | Easily define tools with `@mcp.tool()` decorator |
| Session Management | Optional session state persistence using DynamoDB |
| Type Validation | Automatic validation of function arguments and return values |

### Basic Usage

```python
from awslabs.mcp_lambda_handler import MCPLambdaHandler

mcp = MCPLambdaHandler(
    name="my-mcp-server",
    version="1.0.0",
)

@mcp.tool()
def my_tool(param1: str, param2: int = 10) -> str:
    """Tool description"""
    return f"Result: {param1}, {param2}"

def handler(event, context):
    return mcp.handle_request(event, context)
```

### Supported MCP Methods

| Method | Description |
|--------|-------------|
| `initialize` | Initialize client connection |
| `tools/list` | Return list of registered tools |
| `tools/call` | Execute specified tool |
| `ping` | Health check |

## Setup

### Prerequisites

- Node.js 18+
- Docker (required for Lambda function bundling)
- AWS CLI (configured)

### Deployment

#### API Key Authentication (Default)

```bash
cd cdk
npm install
npx cdk deploy
```

#### OAuth Authentication

```bash
cd cdk
npm install
npx cdk deploy -c authType=oauth
```

#### Specify Custom Project Name

```bash
npx cdk deploy -c projectName=my-mcp-server
npx cdk deploy -c projectName=my-mcp-server -c authType=oauth
```

## Output Values

### Common Outputs

| Output Name | Description |
|-------------|-------------|
| `McpFunctionArn` | Lambda function ARN |
| `McpApiUrl` | API Gateway base URL |
| `McpApiEndpoint` | MCP endpoint (`{ApiUrl}/mcp`) |
| `AuthType` | Authentication type in use |

### Additional Outputs for API Key Authentication

| Output Name | Description |
|-------------|-------------|
| `ApiKeyId` | API Key ID |
| `GetApiKeyCommand` | Command to retrieve API Key value |

### Additional Outputs for OAuth Authentication

| Output Name | Description |
|-------------|-------------|
| `UserPoolId` | Cognito User Pool ID |
| `AppClientId` | Cognito App Client ID |
| `TokenEndpoint` | OAuth 2.0 Token Endpoint URL |
| `OAuthScope` | Scope to use |
| `GetClientSecretCommand` | Command to retrieve Client Secret |

## Post-Deployment Tasks

### For API Key Authentication

#### Retrieve API Key

```bash
# Execute the output command, or run the following
aws apigateway get-api-key \
  --api-key <ApiKeyId> \
  --include-value \
  --query 'value' \
  --output text
```

### For OAuth Authentication

#### Retrieve Client Secret

```bash
# Execute the output GetClientSecretCommand
aws cognito-idp describe-user-pool-client \
  --user-pool-id <UserPoolId> \
  --client-id <AppClientId> \
  --query 'UserPoolClient.ClientSecret' \
  --output text
```

#### Obtain Access Token

```bash
# Obtain token using Client Credentials Flow
curl -X POST "<TokenEndpoint>" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -u "<AppClientId>:<ClientSecret>" \
  -d "grant_type=client_credentials&scope=<OAuthScope>"
```

Response example:
```json
{
  "access_token": "eyJraWQiOi...",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

## Verification

### For API Key Authentication

#### Verification with MCP Inspector

```bash
npx @modelcontextprotocol/inspector \
  --transport streamable-http \
  --url "<McpApiEndpoint>" \
  --header "x-api-key: <API_KEY>"
```

#### Calling tools/list

```bash
curl -X POST "<McpApiEndpoint>" \
  -H "x-api-key: <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }'
```

#### Calling get_schedule Tool

```bash
curl -X POST "<McpApiEndpoint>" \
  -H "x-api-key: <API_KEY>" \
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

### For OAuth Authentication

#### Calling tools/list

```bash
# First obtain access token
ACCESS_TOKEN=$(curl -s -X POST "<TokenEndpoint>" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -u "<AppClientId>:<ClientSecret>" \
  -d "grant_type=client_credentials&scope=<OAuthScope>" \
  | jq -r '.access_token')

# Call API with Bearer token
curl -X POST "<McpApiEndpoint>" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }'
```

#### Calling get_schedule Tool

```bash
curl -X POST "<McpApiEndpoint>" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
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

## MCP Specification Compliance

| Specification | Status |
|---------------|:------:|
| Streamable HTTP | ✅ |
| API Key/Token-based Authentication | ✅ |
| OAuth 2.0 Authentication | ✅ |
| JSON-RPC 2.0 | ✅ |

## Notes

### Credential Management

API keys and OAuth credentials are sensitive information. Please note the following:

- Do not include credentials in code or logs
- Manage securely using AWS Secrets Manager or similar
- Rotate keys as needed

### Docker Requirement

Docker is required to bundle Python dependencies during CDK deployment.

### OAuth Authentication Notes

- Access token expires in 1 hour by default
- Re-execute Client Credentials Flow to refresh tokens
- Scope format is `{projectName}-api/mcp.invoke`


## Security Notice for Sample Implementation

This project is a **sample implementation** and includes debug log output in the Lambda function.

```python
print("event:", json.dumps(event))
```

**For production use, the following actions are required:**

1. **Remove debug logs**: Delete the above log output in `cdk/lambda_python/index.py`. The event object passed from API Gateway contains authentication information such as `x-api-key` and `Authorization` headers, which poses a risk of being recorded in plaintext in CloudWatch Logs.

2. **If logging is required**: Filter sensitive information before logging.
   ```python
   # Bad example: Contains authentication info
   print("event:", json.dumps(event))

   # Good example: Exclude headers
   safe_event = {k: v for k, v in event.items() if k != 'headers'}
   print("event:", json.dumps(safe_event))
   ```

3. **Restrict CloudWatch Logs access**: Limit access to CloudWatch Logs to minimum required using IAM policies.

## References

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [AWS DevOps Agent - MCP Server Configuration](https://docs.aws.amazon.com/devopsagent/latest/userguide/configuring-capabilities-for-aws-devops-agent-connecting-mcp-servers.html)
- [awslabs/mcp-lambda-handler](https://github.com/awslabs/mcp)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector)
- [Amazon Cognito - Client Credentials Grant](https://docs.aws.amazon.com/cognito/latest/developerguide/token-endpoint.html)
