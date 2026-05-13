# =========
# BASE
# =========
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    TZ=UTC

WORKDIR /app

# Paquetes del sistema necesarios
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    netcat-openbsd \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# =========
# DEPENDENCIAS
# =========
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# =========
# APP
# =========
COPY . /app

COPY docker/entrypoint.sh /app/docker/entrypoint.sh
RUN sed -i 's/\r$//' /app/docker/entrypoint.sh && chmod +x /app/docker/entrypoint.sh

# USER appuser

EXPOSE ${PORT:-8000}

ENTRYPOINT ["/app/docker/entrypoint.sh"]

CMD gunicorn Proyecto.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 60