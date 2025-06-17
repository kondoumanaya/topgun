# ベースイメージ - 共通ライブラリを含む
FROM python:3.12.11-slim AS base

# メタデータ
LABEL maintainer="root-bot-team"
LABEL version="1.0"
LABEL description="Root-bot Base Image with topgun library (Python 3.12.11)"

# システム依存関係
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python環境設定
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONOPTIMIZE=2
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1


# 作業ディレクトリ
WORKDIR /app

# 共通依存関係コピーとインストール
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# アプリケーションコード
COPY topgun/ ./topgun/
RUN pip install --no-cache-dir -e ./topgun/

# 共有ユーティリティ
COPY shared/ ./shared/

# PYTHONPATH設定
ENV PYTHONPATH=/app

# ログディレクトリ作成
RUN mkdir -p /app/logs /app/data

# 非rootユーザー作成
RUN useradd -r -s /bin/false -d /app trader && \
    chown -R trader:trader /app

# ユーザー切り替え
USER trader

# デフォルトコマンド
CMD ["python", "--version"]