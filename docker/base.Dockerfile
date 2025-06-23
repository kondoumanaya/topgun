FROM python:3.12.11-slim AS base

# メタデータ 
LABEL maintainer="root-bot-team"
LABEL version="1.0"
LABEL description="Root-bot Base Image with topgun library"

# 早期にセキュリティ設定
RUN groupadd -r trader && useradd -r -g trader trader

# システム依存関係
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 環境変数早期設定
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONOPTIMIZE=2
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONPATH=/app
ENV SETUPTOOLS_SCM_PRETEND_VERSION=1.0.0

WORKDIR /app

# 階層的なインストール
COPY topgun/requirements.txt ./topgun/requirements.txt
RUN pip install --no-cache-dir -r topgun/requirements.txt

COPY topgun/ ./topgun/
RUN pip install --no-cache-dir -e ./topgun/

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコード
COPY shared/ ./shared/

# 必要なディレクトリ
RUN mkdir -p /app/logs /app/data

# 所有権設定
RUN chown -R trader:trader /app

# ユーザー切り替え
USER trader

# デフォルトコマンド
CMD ["python", "--version"]