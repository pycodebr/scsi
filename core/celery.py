import os

from celery import Celery

# Define o módulo de settings padrão do Django para o programa Celery.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('scsi')

# Lê toda a configuração das settings do Django com o prefixo CELERY_.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descobre automaticamente as tasks em <app>/tasks.py de cada app instalada.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Task de diagnóstico: imprime a própria request no worker."""
    print(f'Request: {self.request!r}')
