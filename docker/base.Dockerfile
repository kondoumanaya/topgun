FROM python:3.12-slim
WORKDIR /app
COPY topgun /app/topgun
COPY shared /app/shared
RUN pip install --no-cache-dir -e ./topgun && pip install --no-cache-dir ./shared
