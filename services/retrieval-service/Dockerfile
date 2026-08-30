FROM python:3.12-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY services/retrieval-service/pyproject.toml services/retrieval-service/pyproject.toml
COPY shared/database/pyproject.toml shared/database/pyproject.toml
COPY shared/common/pyproject.toml shared/common/pyproject.toml

RUN pip install --no-cache-dir ./shared/database || true
RUN pip install --no-cache-dir ./shared/common || true

RUN pip install --no-cache-dir ./services/retrieval-service

FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY shared/database /app/shared/database
COPY shared/common /app/shared/common
COPY services/retrieval-service /app/services/retrieval-service

WORKDIR /app/services/retrieval-service

ENV PYTHONPATH=/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
