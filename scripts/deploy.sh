#!/bin/bash
# deploy.sh

set -e

echo "🚀 Sherrinford Bot デプロイ開始..."

# 環境変数確認
if [ -z "$ENVIRONMENT" ]; then
    echo "❌ ENVIRONMENT が設定されていません"
    exit 1
fi

# Docker イメージビルド
echo "📦 Docker イメージビルド中..."
docker-compose -f docker/docker-compose.prod.yml build

# 既存コンテナ停止
echo "🛑 既存コンテナ停止中..."
docker-compose -f docker/docker-compose.prod.yml down

# データベースマイグレーション
echo "🗄️ データベースマイグレーション..."
# python migrate.py

# 新しいコンテナ起動
echo "🔄 新しいコンテナ起動中..."
docker-compose -f docker/docker-compose.prod.yml up -d

# ヘルスチェック
echo "🏥 ヘルスチェック中..."
sleep 10
docker-compose -f docker/docker-compose.prod.yml ps

# 通知
echo "📱 デプロイ完了通知..."
# curl -X POST $SLACK_WEBHOOK -d '{"text":"Sherrinford Bot デプロイ完了"}'

echo "✅ デプロイ完了！"