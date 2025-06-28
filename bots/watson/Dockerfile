FROM root-bot-base:latest
WORKDIR /app/bot
COPY bots/watson /app/bot
RUN pip install --no-cache-dir -r requirements.txt
ENV BOT_NAME=watson
CMD ["python", "-m", "bots.watson.main"]
