# root-bot

Crypto trading bot project with shared topgun library.

## Project Structure

```
root-bot/
├── topgun/                  # 共通非公開パッケージ（pip install -e）
│   ├── topgun/              # 実装
│   ├── requirements.txt     # topgun固有の依存関係
│   └── pyproject.toml       # pip install -e 用
├── bots/
│   └── gmo_board_watcher/   # GMOコイン板情報取得bot
│       ├── main.py
│       ├── requirements.txt
│       └── Dockerfile
├── bot/                     # 既存のbotディレクトリ
│   ├── sherrinford/
│   └── watson/
├── Dockerfile.base          # topgunを含んだ共通ベースイメージ用
├── requirements.txt         # プロジェクト全体の共通依存関係
├── mypy.ini                 # 厳密な型チェック設定
└── README.md

```

## 環境構築

### 1. Python環境の準備

Python 3.12.11以上が必要です：

```bash
pyenv local 3.12.8  # または利用可能な3.12.x
python --version     # Python 3.12.x であることを確認
```

### 2. 依存関係のインストール

以下の順序で依存関係をインストールしてください：

```bash
# 1. topgunの依存関係をインストール
pip install -r topgun/requirements.txt

# 2. topgunをeditable modeでインストール
pip install -e ./topgun

# 3. プロジェクト全体の共通依存関係をインストール
pip install -r requirements.txt

# 4. 特定のbotの依存関係をインストール（例：GMO板情報bot）
pip install -r bots/gmo_board_watcher/requirements.txt
```

### 3. 型チェックの実行

```bash
# プロジェクト全体の型チェック
mypy bots/ topgun/

# 特定のディレクトリのみ
mypy bots/gmo_board_watcher/
```

## Docker運用

### ベースイメージのビルド

```bash
docker build -f Dockerfile.base -t root-bot-base .
```

### GMO板情報botの実行

```bash
# Dockerイメージのビルド
docker build -t gmo-board-watcher bots/gmo_board_watcher/

# コンテナの実行
docker run --rm gmo-board-watcher

# 環境変数を指定して実行
docker run --rm -e GMO_SYMBOL=ETH_JPY gmo-board-watcher
```

## 開発ワークフロー

### 新しいbotの追加

1. `bots/` ディレクトリに新しいbotディレクトリを作成
2. `main.py`, `requirements.txt`, `Dockerfile` を作成
3. topgunライブラリを活用してbot機能を実装
4. 型チェックとDockerビルドテストを実行

### 型安全性の確保

- 全てのPythonファイルで型ヒントを使用
- `mypy --strict` モードで型チェックを通過させる
- topgunライブラリには `py.typed` ファイルが含まれています

### セキュリティ

- 全てのDockerコンテナは非rootユーザー（trader）で実行
- APIキーは環境変数または.envファイルで管理
- ソースコードに機密情報を含めない

## GMO板情報bot

`bots/gmo_board_watcher/` は、GMOコインの板情報を非同期で取得するサンプルbotです。

### 機能

- GMOコインWebSocket APIに接続
- 指定された通貨ペアの板情報を取得
- リアルタイムで板データを標準出力に表示

### 設定

環境変数 `GMO_SYMBOL` で通貨ペアを指定可能（デフォルト: BTC_JPY）

### 実行例

```bash
# ローカル実行
cd bots/gmo_board_watcher
python main.py

# Docker実行
docker run --rm -e GMO_SYMBOL=BTC_JPY gmo-board-watcher
```

## トラブルシューティング

### topgunのインストールエラー

setuptools-scmのバージョン検出エラーが発生する場合：

```bash
export SETUPTOOLS_SCM_PRETEND_VERSION_FOR_TOPGUN=1.0.0
pip install -e ./topgun
```

### 型チェックエラー

厳密な型チェックが有効になっているため、全ての関数に型ヒントが必要です。
`mypy.ini` の設定を確認し、必要に応じて型ヒントを追加してください.
