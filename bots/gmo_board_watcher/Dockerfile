FROM root-bot-base

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

USER trader

CMD ["python", "-O", "main.py"]
