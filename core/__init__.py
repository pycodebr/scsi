# Garante que o app Celery seja carregado quando o Django inicia,
# para que o decorator @shared_task use a instância correta.
from .celery import app as celery_app

__all__ = ('celery_app',)
