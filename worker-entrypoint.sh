#!/bin/sh
set -e

# Entrypoint dos serviços Celery (worker e beat). Diferente do app, NÃO roda
# migrations nem collectstatic — apenas aguarda o banco ficar disponível antes
# de iniciar o processo do Celery. As migrations são aplicadas exclusivamente
# pelo serviço `app` (com advisory lock).

echo ">>> [celery] Aguardando o banco de dados..."
python manage.py wait_for_db --timeout 90

exec "$@"
