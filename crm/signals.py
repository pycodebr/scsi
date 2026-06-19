from django.db.models.signals import post_save
from django.dispatch import receiver

from tenants.models import Brokerage
from .models import Pipeline, Stage

DEFAULT_STAGES = [
    ('Novo Lead', '#17a2b8', 0, False, False),
    ('Contato Inicial', '#6c757d', 1, False, False),
    ('Proposta Enviada', '#ffc107', 2, False, False),
    ('Negociação', '#fd7e14', 3, False, False),
    ('Ganho', '#28a745', 4, True, False),
    ('Perdido', '#dc3545', 5, False, True),
]


@receiver(post_save, sender=Brokerage)
def create_default_pipeline(sender, instance, created, **kwargs):
    if created:
        pipeline = Pipeline.objects.create(
            brokerage=instance,
            name='Pipeline Padrão',
            is_default=True,
        )
        for name, color, order, is_won, is_lost in DEFAULT_STAGES:
            Stage.objects.create(
                brokerage=instance,
                pipeline=pipeline,
                name=name,
                color=color,
                order=order,
                is_won=is_won,
                is_lost=is_lost,
            )