FROM python:3.12-slim

WORKDIR /app

# Copy the specific pyproject.toml
COPY shared/database/pyproject.toml ./shared/database/pyproject.toml
RUN pip install --no-cache-dir ./shared/database

# Copy all shared code
COPY shared/ ./shared/

# Set the working directory to where alembic.ini is
WORKDIR /app/shared/database

ENV PYTHONPATH=/app
CMD ["alembic", "current"]
