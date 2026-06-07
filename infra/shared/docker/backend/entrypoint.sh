#!/usr/bin/env sh
set -eu

cd /app/backend

until python - <<'PY'
import os
import sys

import psycopg2

host = os.environ.get("DB_HOST", "db")
port = int(os.environ.get("DB_PORT", "5432"))
name = os.environ.get("DB_NAME", "registrame_db")
user = os.environ.get("DB_USER", "postgres")
password = os.environ.get("DB_PASSWORD", "")

try:
    conn = psycopg2.connect(
        dbname=name,
        user=user,
        password=password,
        host=host,
        port=port,
        connect_timeout=3,
    )
    conn.close()
except Exception:
    sys.exit(1)
PY
do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

python manage.py migrate --noinput
python manage.py collectstatic --noinput

python - <<'PY'
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "registrame.settings")
django.setup()

from users.models import Role, User

admin_username = os.environ.get("DEFAULT_ADMIN_USERNAME", "admin")
admin_email = os.environ.get("DEFAULT_ADMIN_EMAIL", "admin@registrame.com")
admin_password = os.environ.get("DEFAULT_ADMIN_PASSWORD", "admin123")
admin_full_name = os.environ.get("DEFAULT_ADMIN_FULL_NAME", "Administrador")
admin_dni = os.environ.get("DEFAULT_ADMIN_DNI", "00000000")
admin_phone = os.environ.get("DEFAULT_ADMIN_PHONE", "900000000")

user = User.objects.filter(usuNom=admin_username).first()
if user is None:
    user = User(
        usuNom=admin_username,
        usuEmail=admin_email,
        usuNombreCom=admin_full_name,
        usuDNI=admin_dni,
        usuTel=admin_phone,
        usuEstado=True,
        is_staff=True,
        is_superuser=True,
        is_active=True,
    )
    user.set_password(admin_password)
    user.save()
    print(f"[OK] Usuario admin creado: {admin_username} / {admin_password}")
else:
    updated = False
    if not user.check_password(admin_password):
        user.set_password(admin_password)
        updated = True
    for field, value in (
        ("usuEmail", admin_email),
        ("usuNombreCom", admin_full_name),
        ("usuDNI", admin_dni),
        ("usuTel", admin_phone),
    ):
        if getattr(user, field) != value:
            setattr(user, field, value)
            updated = True
    if not user.is_staff:
        user.is_staff = True
        updated = True
    if not user.is_superuser:
        user.is_superuser = True
        updated = True
    if not user.is_active:
        user.is_active = True
        updated = True
    if updated:
        user.save()
        print(f"[OK] Usuario admin actualizado: {admin_username}")
    else:
        print(f"[INFO] Usuario admin ya existe: {admin_username}")

if user.is_superuser:
    roles = list(Role.objects.all())
    if roles:
        user.roles.set(roles)
PY

exec gunicorn registrame.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
