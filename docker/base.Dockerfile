FROM python:3.12-slim
WORKDIR /app

COPY topgun /app/topgun
COPY shared /app/shared
ENV SETUPTOOLS_SCM_PRETEND_VERSION=1.0.0
RUN pip install --no-cache-dir -e ./topgun
