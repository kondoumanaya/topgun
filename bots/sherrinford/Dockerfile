FROM root-bot-base:latest
WORKDIR /app/bot
COPY bots/sherrinford /app/bot
RUN pip install --no-cache-dir -r requirements.txt
ENV BOT_NAME=sherrinford
CMD ["python", "-m", "bots.sherrinford.main"]
