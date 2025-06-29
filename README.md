# Root-Bot取引システム

完全なボット分離、SQLiteデータベース、Discord通知を備えたモジュラー暗号資産取引ボットシステム。

## アーキテクチャ概要

```
root-bot/
├── bots/                    # 個別取引ボット（完全分離）
│   ├── sherrinford/         # 高頻度スキャルピングボット
│   │   ├── main.py          # ボット実装
│   │   ├── Dockerfile       # 個別コンテナ
│   │   └── requirements.txt # ボット固有の依存関係
│   ├── watson/              # トレンドフォローボット
│   └── gmo_board_watcher/   # GMO板情報監視
├── shared/                  # 共通ライブラリ（軽量）
│   ├── logger.py            # ノンブロッキングI/O用QueueLogging
│   ├── database.py          # aiosqlite付きSQLiteラッパー
│   ├── notifier.py          # Discord専用週次利益レポート
│   └── redis_manager.py     # ボット別オプションRedis
├── topgun/                  # 取引所APIライブラリ（編集可能インストール）
│   └── tests/               # 品質保証テスト（保持）
├── docker/                  # コンテナ設定
│   ├── base.Dockerfile      # 軽量Python 3.12-slimベース
│   ├── docker-compose.yml   # 開発環境
│   └── docker-compose.prod.yml # 本番デプロイ
├── env/                     # 環境設定
│   ├── .env.example         # <FILL_ME>プレースホルダー付きテンプレート
│   ├── sherrinford.env      # 本番設定（Git除外）
│   └── watson.env           # 本番設定（Git除外）
├── .github/workflows/       # CI/CDパイプライン
│   └── ci.yml               # Lint → Test → Build → Deploy
└── docs/                    # ドキュメント
    ├── api_key_guide.md     # APIキー設定手順
    └── architecture.png     # システムアーキテクチャ図
```

## クイックスタート

### 1. 開発環境セットアップ

```bash
# クローンとセットアップ
git clone https://github.com/kondoumanaya/root-bot.git
cd root-bot

# 依存関係をインストール
pip install -e ./topgun
pip install -r requirements.txt

# 環境を設定
cp env/.env.example env/.env.local
# APIキーでenv/.env.localを編集（docs/api_key_guide.mdを参照）
```

### 2. Docker開発

```bash
# ベースイメージをビルド
docker build -f docker/base.Dockerfile -t root-bot-base:latest .

# すべてのボットを開始
docker-compose -f docker/docker-compose.yml up

# 個別ボットを開始
docker-compose -f docker/docker-compose.yml up sherrinford
```

### 3. 本番デプロイ

```bash
# 本番環境（サーバー上）
docker-compose -f docker/docker-compose.prod.yml up -d
```

## 主要機能

### ✅ 完全なボット分離
- 各ボットが独自のSQLiteデータベースを持つ（`/data/<bot>.db`）
- 別々のパスワードとDB番号でボット別オプションRedis
- 分離された依存関係を持つ個別Dockerコンテナ
- ボット間で共有状態なし

### ✅ 高性能ログ
- ノンブロッキングI/O用バックグラウンドスレッド付きQueueLogging
- RotatingFileHandler（最大1MB、3バックアップ）
- 取引ループがログ書き込みでブロックされることなし

### ✅ Discord専用通知
- 毎週月曜日00:00 JSTに週次利益レポート
- シンプルなWebhook統合
- Slack/LINE/メールの複雑さなし

### ✅ 自動化CI/CD
- GitHub Actions: Lint → Test → Build → Deploy
- 全ボットの並列Dockerビルド
- 本番サーバーへのSSHデプロイ
- イメージストレージ用GHCR（GitHub Container Registry）

## 個別ボット実行

```bash
# 直接実行（開発用）
cd bots/sherrinford && python main.py
cd bots/watson && python main.py
cd bots/gmo_board_watcher && python main.py

# Docker実行（推奨）
docker-compose up sherrinford
docker-compose up watson
docker-compose up gmo_board_watcher
```

## 開発ワークフロー

### コード品質
```bash
# LintとType checking
flake8 bots shared
mypy bots shared

# テスト実行
pytest topgun/tests/
```

### 新しいボットの追加
1. テンプレートをコピー: `cp -r bots/template_bot bots/new_bot`
2. 取引ロジックで`bots/new_bot/main.py`を更新
3. 既存パターンに従って`bots/new_bot/Dockerfile`を作成
4. `docker/docker-compose.yml`にサービスを追加
5. 環境ファイルを作成: `env/new_bot.env`
6. `.github/workflows/ci.yml`のCIマトリックスを更新

### データベース管理
- 各ボットは初回実行時に自動的にSQLiteデータベースを作成
- データベースパス: `/data/<bot_name>.db`（`SQLITE_PATH`で設定可能）
- マイグレーション不要 - テーブルは自動作成
- バックアップ: `.db`ファイルを単純にコピー

### Redis使用（オプション）
- ボット環境ファイルで`USE_REDIS=true`を設定
- `REDIS_HOST`、`REDIS_PORT`、`REDIS_PASSWORD`を設定
- 各ボットが分離されたRedisインスタンスまたはDB番号を取得

## セキュリティと設定

### APIキー
- 詳細なセットアップについては[docs/api_key_guide.md](docs/api_key_guide.md)を参照
- 実際のキーをGitにコミットしない
- テンプレートで`<FILL_ME>`プレースホルダーを使用
- 本番キーはGitリポジトリ外に保存

### GitHub Secrets（CI/CD用）
- `GHCR_TOKEN`: GitHub Container Registryアクセス
- `PROD_HOST`: 本番サーバーホスト名
- `PROD_USER`: デプロイ用SSHユーザー名
- `PROD_KEY`: デプロイ用SSH秘密キー

## アーキテクチャの利点

### スケーラビリティ
- 既存のボットに影響を与えずに新しいボットを追加
- ボットを異なるサーバーに独立してデプロイ
- リソースニーズに基づいて個別ボットをスケール

### 信頼性
- ボットの障害が他のボットに影響しない
- データベース破損が単一ボットに分離
- 独立した再起動と復旧

### 保守性
- 明確な関心の分離
- 最小限の共有依存関係
- 個別ボットのデバッグと監視が容易

### パフォーマンス
- ボット間でデータベースロック競合なし
- ノンブロッキングログシステム
- 最小限のオーバーヘッドを持つ軽量コンテナ
