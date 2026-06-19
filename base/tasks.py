from celery import shared_task


@shared_task
def add(x, y):
    """Task de exemplo (Sprint 3) para validar o worker Celery."""
    return x + y
