FROM python:3.12-slim

RUN groupadd -r trader && useradd -r -g trader trader

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ../../topgun ./topgun
RUN pip install -e ./topgun

COPY main.py .

USER trader

ENV PYTHONOPTIMIZE=2
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

CMD ["python", "-O", "main.py"]
