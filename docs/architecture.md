# Root-Bot アーキテクチャ概要

## システム設計

Root-Bot は、ボット間の完全分離、軽量 Docker コンテナ、自動化 CI/CD デプロイを備えたモジュラー取引ボットアーキテクチャを実装しています。

```
┌───────────── root-bot / docker network ─────────────┐
│                                                     │
│   ┌─────────────┐   ┌─────────────┐                 │
│   │ Bot: sherr. │   │ Bot: watson │   … (scalable)  │
│   │  Python/top │   │  Python/top │                 │
│   ├─────────────┤   ├─────────────┤                 │
│   │ /data/*.db  │   │ /data/*.db  │  ← SQLite files │
│   │ Redis(:0)   │   │ Redis(:1)   │  ← Optional     │
│   │ logs/       │   │ logs/       │  ← QueueLogging │
│   └──────┬──────┘   └──────┬──────┘                 │
│          │Discord Webhook (週次利益報告)            │
│          ▼                                         │
└─────────────────────────────────────────────────────┘
```

## 主要コンポーネント

### データベース層

- **ボット別 SQLite**: 各ボットが分離された`/data/<bot>.db`ファイルを維持
- **aiosqlite**: 高性能な非同期データベース操作
- **共有状態ゼロ**: 完全分離によりデータ競合を防止

### キャッシュ層（オプション）

- **ボット別 Redis**: 別々のパスワード/DB 番号を持つオプション Redis インスタンス
- **設定可能**: ボットは`USE_REDIS=false`で Redis を無効化可能

### ログシステム

- **QueueHandler**: 別スレッドを使用したノンブロッキング I/O
- **RotatingFileHandler**: 自動ログローテーション（1MB、3 バックアップ）
- **ボット別ログ**: `/app/logs/<bot>.log`の分離されたログファイル

### 通知システム

- **Discord 専用**: 週次利益レポート用の単一 webhook
- **スケジュール**: 月曜日 00:00 JST（日曜日 15:00 UTC）
- **フォーマット**: `📈 **{bot}** week P/L: +5,000 JPY`

### CI/CD パイプライン

```
GitHub Push → Lint/Test → Docker Build → GHCR Push → SSH Deploy
```

## スケーリング戦略

新しいボットの追加:

1. `bots/template_bot/` → `bots/new_bot/`をコピー
2. `docker-compose.prod.yml`に新しいサービスを更新
3. `.github/workflows/ci.yml`の CI マトリックスにボットを追加
4. `env/new_bot.env`で環境を設定
5. Push → 自動ビルドとデプロイ

## セキュリティモデル

- **GitHub Secrets**: すべての機密データを暗号化されたシークレットに保存
- **環境分離**: 各ボットが別々の`.env`ファイルを持つ
- **共有認証情報なし**: API キー、Redis パスワードをボット別に分離
- **SSH デプロイ**: SSH キーによる安全な自動デプロイ
