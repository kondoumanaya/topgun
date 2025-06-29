# APIキー設定ガイド

## 概要

このガイドでは、Root-Bot取引システムにおいて、開発・本番・CI/CD環境でAPIキーとシークレットを安全に設定する方法を説明します。

## 🔐 セキュリティ原則

1. **Gitにシークレットをコミットしない** - 機密データはすべてバージョン管理から除外
2. **環境分離** - 開発・ステージング・本番で異なるキーを使用
3. **最小権限** - 各ボットは必要なキーのみを取得
4. **暗号化ストレージ** - CI/CD自動化にはGitHub Secretsを使用

## 📁 ファイル構造

```
root-bot/
├── env/
│   ├── .env.example          # プレースホルダー値付きテンプレート
│   ├── .env.local           # 開発用（Git除外）
│   ├── sherrinford.env      # 本番ボット設定（Git除外）
│   ├── watson.env           # 本番ボット設定（Git除外）
│   └── gmo_board_watcher.env # 本番ボット設定（Git除外）
└── docs/
    └── api_key_guide.md     # このファイル
```

## 🛠️ 開発環境セットアップ

### ステップ1: テンプレートをコピー
```bash
cd root-bot/
cp env/.env.example env/.env.local
```

### ステップ2: 開発用の値を入力
`env/.env.local`を編集:
```bash
# 取引APIキー（開発にはテストネット/サンドボックスキーを使用）
API_KEY_BTC_JPY=your_development_api_key_here
API_SECRET_BTC_JPY=your_development_secret_here

# データベース
SQLITE_PATH=/data/dev_bot.db

# 通知（開発時はオプション）
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/123456789/your_dev_webhook

# Redis（オプション）
USE_REDIS=true
REDIS_PASSWORD=dev_redis_password
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# 環境設定
ENVIRONMENT=development
BOT_NAME=dev_bot
```

### ステップ3: 設定をテスト
```bash
# 環境変数が正しく読み込まれることを確認
python -c "
import os
from dotenv import load_dotenv
load_dotenv('env/.env.local')
print('API Key loaded:', bool(os.getenv('API_KEY_BTC_JPY')))
print('Environment:', os.getenv('ENVIRONMENT'))
"
```

## 🚀 本番デプロイ

### サーバーセットアップ

1. **本番サーバーでボット専用環境ファイルを作成**:
```bash
# 本番サーバー上: /srv/root-bot/env/
sudo mkdir -p /srv/root-bot/env
```

2. **sherrinford.envを設定**:
```bash
# /srv/root-bot/env/sherrinford.env
API_KEY_BTC_JPY=live_api_key_for_sherrinford
API_SECRET_BTC_JPY=live_secret_for_sherrinford
SQLITE_PATH=/data/sherrinford.db
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/prod/sherrinford_webhook
USE_REDIS=true
REDIS_PASSWORD=secure_sherrinford_redis_password
REDIS_HOST=sherrinford-redis
REDIS_PORT=6379
REDIS_DB=0
ENVIRONMENT=production
BOT_NAME=sherrinford
```

3. **watson.envを設定**:
```bash
# /srv/root-bot/env/watson.env
API_KEY_BTC_JPY=live_api_key_for_watson
API_SECRET_BTC_JPY=live_secret_for_watson
SQLITE_PATH=/data/watson.db
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/prod/watson_webhook
USE_REDIS=false  # WatsonはRedisを必要としない
ENVIRONMENT=production
BOT_NAME=watson
```

### ファイル権限
```bash
# 環境ファイルを保護
sudo chown root:docker /srv/root-bot/env/*.env
sudo chmod 640 /srv/root-bot/env/*.env
```

## 🔄 CI/CD設定

### GitHub Secrets設定

リポジトリに移動: **Settings** → **Secrets and variables** → **Actions**

以下のシークレットを追加:

#### コンテナレジストリ
```
GHCR_TOKEN=ghp_your_github_personal_access_token
```
*必要な権限: `read:packages`, `write:packages`*

#### デプロイ用SSH
```
PROD_HOST=your.production.server.ip
PROD_USER=deploy_user
PROD_KEY=-----BEGIN OPENSSH PRIVATE KEY-----
your_ssh_private_key_content_here
-----END OPENSSH PRIVATE KEY-----
```

### SSHキー生成
```bash
# デプロイ用キーペアを生成
ssh-keygen -t ed25519 -f ~/.ssh/root_bot_deploy -C "root-bot-deploy"

# 公開キーを本番サーバーにコピー
ssh-copy-id -i ~/.ssh/root_bot_deploy.pub deploy_user@your.server.ip

# 秘密キーの内容をGitHub SecretsのPROD_KEYにコピー
cat ~/.ssh/root_bot_deploy
```

## 🔧 APIキーの取得先

### 暗号資産取引所

#### GMO Coin
1. GMO Coinアカウントにログイン
2. **API** → **APIキー管理**に移動
3. 以下の権限で新しいAPIキーを作成:
   - ✅ Private API（取引用）
   - ✅ WebSocket Private API
   - ❌ 出金（不要）
4. APIキーとシークレットを即座にコピー
5. 本番サーバー用にIPホワイトリストを設定

#### その他の取引所
他のサポート対象取引所でも同様の手順。常に以下を使用:
- **テストネット/サンドボックス**キーを開発用に
- **本番**キーは本番サーバーでのみ
- **最小権限**（取引のみ、出金なし）

### Discord Webhook

#### Discord Webhookの作成
1. Discordサーバーを開く → チャンネル設定
2. **連携サービス** → **ウェブフック** → **新しいウェブフック**
3. 名前: `Root-Bot-{ボット名}-{環境}`
4. Webhook URLをコピー
5. curlでテスト:
```bash
curl -X POST "YOUR_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"content": "🤖 Root-Bot テストメッセージ"}'
```

## 🚨 セキュリティベストプラクティス

### APIキーセキュリティ
- ✅ 各ボットで異なるキーを使用
- ✅ 開発にはテストネットキーを使用
- ✅ 定期的にキーをローテーション（四半期ごと）
- ✅ API使用量の異常を監視
- ❌ 環境間でキーを共有しない
- ❌ Gitにキーをコミットしない
- ❌ ローカルで本番キーを使用しない

### 環境ファイルセキュリティ
```bash
# .gitignoreに追加（既に設定済み）
env/.env.local
env/*.env
!env/.env.example

# Gitにシークレットがないことを確認
git log --all --full-history -- env/ | grep -i "secret\|key\|password"
```

### アクセス制御
- 本番サーバーアクセスはデプロイユーザーに限定
- GitHub Secretsアクセスはリポジトリ管理者に限定
- APIキーは必要最小限の権限で設定
- アクセスログの定期監査

## 🔍 トラブルシューティング

### よくある問題

#### "API Key not found"
```bash
# 環境変数の読み込みを確認
python -c "
import os
from dotenv import load_dotenv
load_dotenv('env/sherrinford.env')
print('Keys loaded:', [k for k in os.environ.keys() if 'API' in k])
"
```

#### "Discord webhook failed"
```bash
# Webhookを手動でテスト
curl -X POST "$DISCORD_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"content": "curlからのテスト"}'
```

#### "Redis connection failed"
```bash
# Redis接続性を確認
redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD ping
```

### 検証スクリプト
```python
#!/usr/bin/env python3
"""Root-Bot環境設定を検証"""
import os
from dotenv import load_dotenv

def validate_env(env_file):
    load_dotenv(env_file)
    required_keys = [
        'API_KEY_BTC_JPY', 'API_SECRET_BTC_JPY', 
        'SQLITE_PATH', 'BOT_NAME', 'ENVIRONMENT'
    ]
    
    missing = [key for key in required_keys if not os.getenv(key)]
    if missing:
        print(f"❌ {env_file}に不足キー: {missing}")
        return False
    
    print(f"✅ {env_file} 設定は有効")
    return True

# すべての環境ファイルを検証
for env_file in ['env/.env.local', 'env/sherrinford.env', 'env/watson.env']:
    if os.path.exists(env_file):
        validate_env(env_file)
```

## ボット固有の設定

### Sherrinfordボット
- **目的**: 高度な戦略による高頻度取引
- **データベース**: `/data/sherrinford.db` (SQLite)
- **Redis**: キャッシュに必要 (`USE_REDIS=true`)
- **環境設定**: `env/sherrinford.env`
- **Discord**: 取引通知専用webhook

### Watsonボット  
- **目的**: 中頻度分析取引
- **データベース**: `/data/watson.db` (SQLite)
- **Redis**: 不要 (`USE_REDIS=false`)
- **環境設定**: `env/watson.env`
- **Discord**: 分析レポート用webhook

### GMO Board Watcher
- **目的**: 市場監視とデータ収集
- **データベース**: `/data/gmo_board_watcher.db` (SQLite)
- **Redis**: データキャッシュ用（オプション）
- **環境設定**: `env/gmo_board_watcher.env`
- **Discord**: 監視アラートとサマリー

## 📞 サポート

追加のヘルプについて:
1. [アーキテクチャガイド](architecture.md)を確認
2. `bots/*/README.md`のボット固有ドキュメントを確認
3. `env/.env.example`の動作例を確認
4. 上記の検証スクリプトで設定をテスト

---

**⚠️ 注意: すべてのAPIキーとシークレットを安全に保管してください。疑問がある場合は、リスクを冒すよりもキーを再生成してください。**
