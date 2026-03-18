#!/usr/bin/env bash
set -e

# Espera a la DB (si es Postgres). Puedes usar wait-for-it o psql simple:
if [ "$POSTGRES_HOST" != "" ]; then
  echo "Esperando a la base de datos en $POSTGRES_HOST:$POSTGRES_PORT..."
  until nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
    sleep 1
  done
fi

echo "Aplicando migraciones..."
python manage.py migrate --noinput

echo "Levantando servidor..."

# exec python manage.py runserver 0.0.0.0:8000
exec gunicorn Proyecto.wsgi:application --bind 0.0.0.0:8000 --workers 3