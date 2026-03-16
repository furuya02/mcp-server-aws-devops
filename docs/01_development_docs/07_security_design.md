# セキュリティ設計

## 概要

本プロジェクトは AWS のセキュリティベストプラクティスに従い、多層防御のアプローチでセキュリティを実装しています。

## セキュリティアーキテクチャ

### 全体像

```
                         HTTPS
Client ──────────────────────────> API Gateway
                                        │
                                   認証チェック
                                   (API Key / OAuth)
                                        │
                                        v
                                   Lambda Function
                                   (VPC 外)
                                        │
                                   X-Ray トレーシング
                                        │
                                        v
                                   CloudWatch Logs
```

## 認証・認可

### API Key 認証

| セキュリティ機能 | 実装 |
|----------------|------|
| 認証 | API Gateway API Key |
| レート制限 | Usage Plan |
| 転送時暗号化 | HTTPS 必須 |

### OAuth 認証

| セキュリティ機能 | 実装 |
|----------------|------|
| 認証 | Cognito Client Credentials Flow |
| 認可 | スコープベースのアクセス制御 |
| トークン有効期限 | 1 時間 |
| Token Revocation | 有効 |

## 通信セキュリティ

### HTTPS 通信

- API Gateway は HTTPS エンドポイントのみを提供
- TLS 1.2 以上を使用
- AWS 管理の証明書

### CORS 設定

```typescript
defaultCorsPreflightOptions: {
  allowOrigins: apigateway.Cors.ALL_ORIGINS,
  allowMethods: apigateway.Cors.ALL_METHODS,
}
```

**注意:** 本番環境では `allowOrigins` を特定のオリジンに制限することを推奨します。

## 認証情報の管理

### ベストプラクティス

| 項目 | 推奨事項 |
|------|---------|
| API Key | AWS CLI コマンドで取得、コードに含めない |
| Client Secret | AWS CLI コマンドで取得、環境変数で管理 |
| ローテーション | 定期的にキー/シークレットを更新 |
| 保管 | AWS Secrets Manager の使用を推奨 |

### やってはいけないこと

- 認証情報をソースコードにハードコード
- 認証情報をログに出力
- 認証情報を Git にコミット
- 認証情報を平文で保存

## Lambda セキュリティ

### 実行ロール

CDK が自動生成する最小権限のロールを使用。

### 環境変数

機密情報を環境変数に含める場合は、AWS Secrets Manager または Parameter Store を使用。

### ログ出力

```python
# イベントのログ出力時は機密情報に注意
print("event:", json.dumps(event))
```

**注意:** 本番環境では、認証ヘッダーなど機密情報のマスキングを検討してください。

## API Gateway セキュリティ

### スロットリング

API Key 認証時の Usage Plan 設定：

| 設定 | 値 | 目的 |
|------|-----|------|
| Rate Limit | 100 req/sec | DoS 攻撃の緩和 |
| Burst Limit | 200 req | 一時的なスパイク対応 |

### リクエスト検証

- JSON-RPC 2.0 形式のリクエストのみ処理
- 不正なリクエストは拒否

## 監視・監査

### CloudWatch Logs

| ログ | 内容 |
|------|------|
| Lambda ログ | 関数の実行ログ |
| API Gateway ログ | アクセスログ（オプション） |

### X-Ray トレーシング

```typescript
tracing: lambda.Tracing.ACTIVE
```

- リクエストの追跡
- パフォーマンス分析
- エラー調査

## コンプライアンス

### AWS 準拠

- AWS のセキュリティベストプラクティスに準拠
- IAM 最小権限の原則
- 保存時および転送時の暗号化

### MCP 仕様準拠

| 仕様 | 対応 |
|------|------|
| VPC 内ホスト未サポート | ✅（VPC 設定なし） |
| 認証必須 | ✅ |
| HTTPS | ✅ |

## セキュリティチェックリスト

### デプロイ前

- [ ] AWS 認証情報が適切に設定されている
- [ ] Docker が最新バージョン
- [ ] 依存関係に脆弱性がない

### デプロイ後

- [ ] API Key / Client Secret が安全に管理されている
- [ ] 不要な API Key / トークンが削除されている
- [ ] ログに機密情報が含まれていない
- [ ] アクセスが意図したクライアントのみに制限されている

### 定期メンテナンス

- [ ] 依存関係の更新
- [ ] API Key / Client Secret のローテーション
- [ ] ログの監視とアラート設定
- [ ] 異常なアクセスパターンの確認

## セキュリティインシデント対応

### API Key 漏洩時

1. API Key を無効化
2. 新しい API Key を作成
3. クライアントに新しいキーを配布
4. アクセスログを確認

```bash
# API Key の無効化
aws apigateway update-api-key \
  --api-key {ApiKeyId} \
  --patch-operations op=replace,path=/enabled,value=false
```

### Client Secret 漏洩時

1. 新しい App Client を作成
2. 古い App Client を削除
3. クライアントに新しい認証情報を配布
4. アクセスログを確認

## 推奨セキュリティ強化

### 本番環境向け

1. **WAF の追加**
   - SQL インジェクション対策
   - XSS 対策
   - レート制限の強化

2. **VPC エンドポイント**
   - プライベートネットワークからのアクセス

3. **CloudTrail**
   - API 呼び出しの監査ログ

4. **GuardDuty**
   - 脅威検出

5. **CORS の制限**
   - 特定オリジンのみ許可
