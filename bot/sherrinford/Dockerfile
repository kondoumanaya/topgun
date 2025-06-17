# bots/sherrinford/Dockerfile
FROM root-bot-base:latest

WORKDIR /app
ENV BOT_NAME=sherrinford

# ボット固有の依存関係
COPY bots/${BOT_NAME}/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ボット固有のコード
COPY bots/${BOT_NAME}/ ./bots/${BOT_NAME}/

# 実行
CMD ["python", "-m", "bots.sherrinford.main"]