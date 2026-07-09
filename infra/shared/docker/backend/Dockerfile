FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app/backend

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY infra/shared/docker/backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt

COPY backend /app/backend
COPY database_seed.sql /app/database_seed.sql
COPY infra/shared/docker/backend/entrypoint.sh /app/infra/shared/docker/backend/entrypoint.sh
RUN chmod +x /app/infra/shared/docker/backend/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/infra/shared/docker/backend/entrypoint.sh"]
