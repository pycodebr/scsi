#!/bin/sh
set -e

# Entrypoint do serviço web (app). O Docker Swarm ignora depends_on em runtime,
# então aguardamos o banco e aplicamos migrations de forma segura mesmo com
# várias réplicas, usando um advisory lock do PostgreSQL (só uma réplica migra
# por vez; as demais aguardam e seguem).

echo ">>> Aguardando o banco de dados..."
python manage.py wait_for_db --timeout 90

echo ">>> Aplicando migrations (com advisory lock para multi-réplica)..."
python <<'PY'
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.management import call_command
from django.db import connection

if connection.vendor == 'postgresql':
    with connection.cursor() as cursor:
        cursor.execute('SELECT pg_try_advisory_lock(1)')
        acquired = cursor.fetchone()[0]
        if acquired:
            try:
                print('>>> Lock adquirido — executando migrations...')
                call_command('migrate', '--noinput')
            finally:
                cursor.execute('SELECT pg_advisory_unlock(1)')
            print('>>> Migrations concluídas e lock liberado.')
        else:
            print('>>> Outra réplica está migrando — aguardando o lock...')
            cursor.execute('SELECT pg_advisory_lock(1)')
            cursor.execute('SELECT pg_advisory_unlock(1)')
            print('>>> Migrations concluídas pela outra réplica.')
else:
    call_command('migrate', '--noinput')
PY

echo ">>> Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear

exec "$@"
