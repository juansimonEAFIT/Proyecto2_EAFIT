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

echo "Creando superusuario por defecto si no existe..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
u, created = User.objects.get_or_create(username='admin', defaults={'email':'admin@lunchflow.com', 'role':'administrador'})
if created:
    u.set_password('admin123')
    u.save()
    from users.models import Administrador
    Administrador.objects.get_or_create(user=u, cargo='Super Admin')
"

echo "Obteniendo contenido estatico..."
python manage.py collectstatic --noinput

echo "Levantando servidor..."

# exec python manage.py runserver 0.0.0.0:8000
PORT="${PORT:-8000}"
exec gunicorn Proyecto.wsgi:application --bind 0.0.0.0:$PORT --workers 3
