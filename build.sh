#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Instalando dependencias..."
pip install -r requirements.txt

echo "Ejecutando migraciones..."
python manage.py migrate --noinput

echo "Creando superusuario por defecto..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
try:
    User = get_user_model()
    u, created = User.objects.get_or_create(username='admin', defaults={'email':'admin@lunchflow.com', 'role':'administrador'})
    if created:
        u.set_password('admin123')
        u.save()
        from users.models import Administrador
        Administrador.objects.get_or_create(user=u, cargo='Super Admin')
        print('Superusuario creado con exito.')
except Exception as e:
    print('Error al crear superusuario:', e)
"

echo "Recolectando estaticos..."
python manage.py collectstatic --noinput
