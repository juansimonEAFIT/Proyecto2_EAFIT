# =========
# BASE
# =========
FROM python:3.12-slim AS base

# Evita .pyc y fuerza logs en stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    TZ=UTC

# Directorio de trabajo
WORKDIR /app

# Paquetes del sistema necesarios para compilación y runtime:
# - build-essential y gcc: compilar dependencias (psycopg2/Pillow)
# - libpq-dev/libpq5: PostgreSQL client libs
# - libjpeg, zlib, freetype, webp, tiff: soporte imágenes para Pillow
# - netcat-traditional: para esperar DB (si lo necesitas)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        libpq-dev \
        libpq5 \
        netcat-traditional \
        libjpeg62-turbo-dev \
        zlib1g-dev \
        libfreetype6-dev \
        libwebp-dev \
        libtiff5 \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# =========
# DEPENDENCIAS
# =========
# Copiamos solo requirements primero para aprovechar la caché
COPY requirements.txt /app/requirements.txt

# Si usas Poetry/Pipenv, dímelo y te doy un Dockerfile ajustado
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# =========
# APP
# =========
# Copiamos el resto del código
COPY . /app

# Crear usuario no root
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser && \
    chown -R appuser:appgroup /app

USER appuser

# Puerto por defecto (Gunicorn/Django)
EXPOSE 8000

# Variables típicas (ajústalas en compose/entorno)
ENV DJANGO_SETTINGS_MODULE=myproject.settings \
    DJANGO_SUPERUSER_USERNAME=admin \
    DJANGO_SUPERUSER_EMAIL=admin@example.com

# Script de arranque (migraciones + collectstatic + Gunicorn)
# Puedes comentar lo que no necesites
ENTRYPOINT ["/app/entrypoint.sh"]

# Por defecto, ejecuta gunicorn (verás que exec en entrypoint lo llama)
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60"]