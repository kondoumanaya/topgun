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

# 開発用依存関係
pip install -r requirements/test.txt
pip install -r requirements/typing.txt
```

### 3. 環境設定
```bash
# 環境変数設定
cp env/.env.example env/.env
cp env/.env.example env/.env.local

# APIキーなどの秘密情報を設定
vim env/.env.local
```

### 4. データベース設定（Docker使用時）
```bash
# 開発環境起動
docker-compose -f docker/docker-compose.yml up postgres redis -d

# データベース初期化
# （必要に応じてマイグレーション実行）
```

## 各ボットの個別セットアップ

### GMO板情報取得ボット
```bash
cd bots/gmo_board_watcher
pip install -r requirements.txt

# 環境変数設定
export GMO_SYMBOL=BTC_JPY

# 実行
python main.py
```

### Sherrinfordボット
```bash
cd bots/sherrinford
pip install -r requirements.txt

# 設定ファイル確認
vim config.yml

# 実行
python main.py
```

### Watsonボット
```bash
cd bots/watson
pip install -r requirements.txt

# 設定ファイル確認
vim config.yml

# 実行
python main.py
```

## Docker環境セットアップ

### 開発環境
```bash
docker-compose -f docker/docker-compose.yml up
```

### テスト環境
```bash
docker-compose -f docker/docker-compose.test.yml up --profile test
```

### 本番環境
```bash
# 本番用環境変数設定
cp env/.env.example env/.env.production
vim env/.env.production

# 本番環境起動
docker-compose -f docker/docker-compose.prod.yml up -d
```

## トラブルシューティング

### topgunインポートエラー
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
