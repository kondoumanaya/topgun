FROM root-bot-base:latest
WORKDIR /app/bot
COPY bots/gmo_board_watcher /app/bot
RUN pip install --no-cache-dir -r requirements.txt
ENV BOT_NAME=gmo_board_watcher
CMD ["python", "-m", "bots.gmo_board_watcher.main"]
