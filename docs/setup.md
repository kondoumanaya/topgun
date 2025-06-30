# セットアップガイド

## 前提条件

- Python 3.12.11
- Docker & Docker Compose
- Git

## 初回セットアップ

### 1. リポジトリクローン

```bash
git clone https://github.com/kondoumanaya/root-bot.git
cd root-bot
```

### 2. 依存関係インストール

```bash
# topgunライブラリ（editable install）
pip install -e ./topgun

# プロジェクト共通依存関係
pip install -r requirements.txt

# 本番用依存関係のみ
```

### 3. 環境設定

```bash
# 環境変数設定
cp env/.env.example env/.env.production

# APIキーなどの秘密情報を設定
vim env/.env.production
```

#### 環境変数管理の詳細

**ファイル構成と役割**:

- `env/.env.example`: 設定テンプレート（Git 管理対象）
- `env/.env.production`: 本番環境用（Git 管理対象外）

**読み込み優先順位**:

1. `.env.production` (最優先)
2. `.env.example`

**各ボットでの使用方法**:

```python
from dotenv import load_dotenv
import os

# 環境変数を明示的にロード
load_dotenv("env/.env.production")
load_dotenv("env/.env.example")

# APIキーの取得
api_key = os.getenv("GMO_API_KEY")
```

### 4. 本番環境起動

```bash
# 本番環境起動
docker-compose up -d
```

## 各ボットの個別セットアップ

### GMO 板情報取得ボット

```bash
cd bots/gmo_board_watcher
pip install -r requirements.txt

# 環境変数設定
export GMO_SYMBOL=BTC_JPY

# 実行
python main.py
```

### Sherrinford ボット

```bash
cd bots/sherrinford
pip install -r requirements.txt

# 設定ファイル確認
vim config.yml

# 実行
python main.py
```

### Watson ボット

```bash
cd bots/watson
pip install -r requirements.txt

# 設定ファイル確認
vim config.yml

# 実行
python main.py
```

## Docker 本番環境セットアップ

### 本番環境

```bash
# 本番用環境変数設定
cp env/.env.example env/.env.production
vim env/.env.production

# 本番環境起動
docker-compose up -d
```

## shared/ ディレクトリの活用

### API キー管理

```python
# 各ボットでのAPIキー使用例
from shared.api_keys import api_keys

# GMOコインのAPIキーを取得
gmo_api_key, gmo_secret = api_keys.get_gmo_credentials()

# 必要なキーが設定されているかチェック
if api_keys.validate_keys(["gmo_api_key", "gmo_secret_key"]):
    # ボット処理を開始
    pass
```

### 共通関数の使用

```python
# 共通モジュールのインポート
from shared.logger import setup_logger
from shared.database import DatabaseManager
from shared.notifier import NotificationManager
from shared.monitoring import MetricsCollector

# 各ボットで共通機能を活用
logger = setup_logger("bot_name")
db = DatabaseManager()
notifier = NotificationManager()
metrics = MetricsCollector("bot_name")
```

## トラブルシューティング

### topgun インポートエラー

```bash
# editable installの再実行
pip install -e ./topgun --force-reinstall

# PYTHONPATHの確認
export PYTHONPATH=$(pwd):$PYTHONPATH
```

### 型チェックエラー

```bash
# mypyの実行
mypy bots/ shared/

# 型スタブの更新
pip install --upgrade types-PyYAML types-requests
```
