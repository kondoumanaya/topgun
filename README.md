# Root-Bot Trading System

高性能な仮想通貨取引ボットシステム。各ボットが独立したコンテナで動作し、共通ライブラリ`topgun`を活用します。

## プロジェクト構成

```
root-bot/
├── env/                     # 環境変数管理
│   ├── .env                 # 基本設定
│   ├── .env.local           # ローカル開発用
│   ├── .env.production      # 本番環境用
│   └── .env.example         # 設定テンプレート
├── bots/                    # 各ボット実装
│   ├── gmo_board_watcher/   # GMO板情報取得ボット
│   ├── sherrinford/         # 高頻度スキャルピングボット
│   └── watson/              # トレンドフォローボット
├── shared/                  # 共通モジュール
│   ├── logger.py            # ログ管理
│   ├── database.py          # データベース管理
│   ├── notifier.py          # 通知管理
│   ├── monitoring.py        # メトリクス収集
│   └── redis_manager.py     # Redis管理
├── topgun/                  # 共通ライブラリ（editable install）
├── docker/                  # Docker設定
│   ├── docker-compose.yml   # 開発環境
│   ├── docker-compose.test.yml  # テスト環境
│   └── docker-compose.prod.yml  # 本番環境
├── config/                  # 設定ファイル
└── docs/                    # ドキュメント
```

## セットアップ手順

### 1. 依存関係のインストール

```bash
# 1. topgunをeditable installでインストール
pip install -e ./topgun

# 2. プロジェクト共通依存関係
pip install -r requirements.txt

# 3. 各ボット固有の依存関係（必要に応じて）
pip install -r bots/gmo_board_watcher/requirements.txt
pip install -r bots/sherrinford/requirements.txt
pip install -r bots/watson/requirements.txt
```

### 2. 環境設定

```bash
# 設定テンプレートをコピー
cp env/.env.example env/.env
cp env/.env.example env/.env.local

# 必要な環境変数を設定
vim env/.env.local
```

### 3. Docker環境での実行

```bash
# 開発環境
docker-compose -f docker/docker-compose.yml up

# テスト環境
docker-compose -f docker/docker-compose.test.yml up --profile test

# 本番環境
docker-compose -f docker/docker-compose.prod.yml up
```

## ボット個別実行

### GMO板情報取得ボット
```bash
cd bots/gmo_board_watcher
python main.py
```

### Sherrinfordボット（高頻度取引）
```bash
cd bots/sherrinford  
python main.py
```

### Watsonボット（トレンドフォロー）
```bash
cd bots/watson
python main.py
```

## 開発ガイド

### 型チェック
```bash
mypy bots/ shared/
```

### テスト実行
```bash
pytest tests/
```

### 新しいボットの追加
1. `bots/new_bot/` ディレクトリを作成
2. `main.py`, `requirements.txt`, `Dockerfile` を実装
3. `docker-compose.yml` にサービスを追加
4. 共通モジュール（shared/）を活用
