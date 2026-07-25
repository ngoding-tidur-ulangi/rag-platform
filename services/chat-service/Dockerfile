FROM python:3.12-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY services/chat-service/pyproject.toml services/chat-service/pyproject.toml
COPY shared/database/pyproject.toml shared/database/pyproject.toml

RUN pip install --no-cache-dir ./shared/database || true

RUN pip install --no-cache-dir ./services/chat-service

FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY shared/database /app/shared/database
COPY services/chat-service /app/services/chat-service

WORKDIR /app/services/chat-service

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
