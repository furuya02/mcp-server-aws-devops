# プロジェクト概要

## 概要

本プロジェクトは、**AWS DevOps Agent** から使用するための MCP サーバーを Lambda で構築するものです。AWS CDK でインフラを管理します。

以下の AWS ドキュメントに基づき、必要な仕様を満たす実装となっています：

- [Configuring capabilities for AWS DevOps Agent: Connecting MCP servers](https://docs.aws.amazon.com/devopsagent/latest/userguide/configuring-capabilities-for-aws-devops-agent-connecting-mcp-servers.html)

### 対応仕様

| 要件 | 対応状況 |
|------|:--------:|
| Streamable HTTP トランスポート | ✅ |
| API キー/トークンベースの認証 | ✅ (スイッチで選択)|
| OAuth 2.0 認証 (Client Credentials Flow) | ✅ (スイッチで選択)|
| VPC 内ホスト未サポート | ✅ (VPC内ホストは、DevOps Agentで未サポート) |
| JSON-RPC 2.0 | ✅ |

## 目的

- **AWS DevOps Agent** から利用可能な MCP Server の実装
- AWS Lambda を使用したサーバーレス MCP Server の実装例を提供
- API Key 認証と OAuth 2.0 認証の2つの認証方式をサポート
- AWS CDK によるインフラストラクチャのコード化
- awslabs.mcp_lambda_handler ライブラリの活用例を示す

## サーバー情報

| 項目 | 値 |
|------|-----|
| サーバー名 | `service-operations-mcp` |
| バージョン | `1.0.0` |
| プロトコル | Streamable HTTP |
| ランタイム | Python 3.12 |

## 主な機能

### 提供ツール

本プロジェクトはサンプル実装のため、**最小限の Tool のみ**を提供しています。

| ツール名 | 説明 | 引数 | 戻り値 |
|---------|------|------|--------|
| `get_schedule` | サービス運用のスケジュールを取得 | なし | JSON |

実際のプロジェクトでは、`cdk/lambda_python/index.py` に Tool を追加して拡張してください。

### 認証方式

| 認証タイプ | 説明 | 認証方法 |
|----------|------|----------|
| `api-key` (デフォルト) | API Key 認証 | `x-api-key` ヘッダー |
| `oauth` | OAuth 2.0 (Client Credentials) | `Authorization: Bearer <token>` ヘッダー |

## 技術スタック

### インフラストラクチャ

- **AWS CDK** (v2.238.0) - Infrastructure as Code
- **TypeScript** (5.4.0) - CDK コード言語
- **Node.js / pnpm** - 依存関係管理

### ランタイム

- **AWS Lambda** - サーバーレスコンピューティング (Python 3.12)
- **AWS API Gateway** - REST API
- **AWS Cognito** - OAuth 2.0 IdP (オプション)
- **AWS CloudWatch** - X-Ray トレーシング

### MCP フレームワーク

- **awslabs.mcp_lambda_handler** - AWS Labs MCP ライブラリ
- **Streamable HTTP** - MCP トランスポートプロトコル
- **JSON-RPC 2.0** - メッセージプロトコル

## プロジェクト構成

```
mcp-server-aws-devops/
├── assets/                          # アーキテクチャ図
│   ├── architecture-api-key.drawio
│   ├── architecture-api-key.png
│   ├── architecture-oauth.drawio
│   └── architecture-oauth.png
├── cdk/                             # CDK プロジェクト
│   ├── bin/
│   │   └── cdk.ts                   # CDK エントリーポイント
│   ├── lib/
│   │   └── mcp-stack.ts             # メインスタック
│   ├── lambda_python/
│   │   ├── index.py                 # Lambda 関数実装
│   │   └── requirements.txt         # Python 依存関係
│   ├── cdk.json                     # CDK 設定
│   ├── package.json                 # Node.js 依存関係
│   └── tsconfig.json                # TypeScript 設定
├── docs/                            # 技術ドキュメント
├── README.md                        # プロジェクト README
└── CLAUDE.md                        # Claude Code 設定
```

## 前提条件

- Node.js 18+
- Docker（Lambda 関数のバンドリングに必要）
- AWS CLI（設定済み）
- pnpm（推奨）または npm

## 関連リンク

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [AWS DevOps Agent - MCP Server Configuration](https://docs.aws.amazon.com/devopsagent/latest/userguide/configuring-capabilities-for-aws-devops-agent-connecting-mcp-servers.html)
- [awslabs/mcp-lambda-handler](https://github.com/awslabs/mcp)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector)
- [Amazon Cognito - Client Credentials Grant](https://docs.aws.amazon.com/cognito/latest/developerguide/token-endpoint.html)
