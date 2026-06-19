from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import LineOfBusiness


DEFAULT_LOBS = [
    ('Auto', 'auto', 'Auto'),
    ('Auto Compreensivo', '', 'auto'),
    ('RCF-V', '', 'auto'),
    ('Vida em Grupo', '', 'life'),
    ('Vida Individual', '', 'life'),
    ('Residencial', '', 'property'),
    ('Incêndio', '', 'property'),
    ('Empresarial', '', 'business'),
    ('RC Empresarial', '', 'business'),
    ('Viagem Nacional', '', 'travel'),
    ('Viagem Internacional', '', 'travel'),
    ('Saúde - PME', '', 'health'),
    ('Saúde Individual', '', 'health'),
]


@receiver(post_save, sender='tenants.Brokerage')
def seed_default_lobs(sender, instance, created, **kwargs):
    """Cria ramos padrão ao criar uma corretora (seed de onboarding).

    Só executa na criação (created=True), garantindo que corretoras
    novas já tenham os ramos mais comuns disponíveis.
    """
    if not created:
        return

    for name, code, category in DEFAULT_LOBS:
        LineOfBusiness.objects.get_or_create(
            brokerage=instance,
            name=name,
            defaults={'code': code, 'category': category},
        )