from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import Plan


@receiver(post_migrate)
def seed_plans(sender, **kwargs):
    """Cria o plano Free na primeira migração do app tenants.

    Os demais planos (Pro, Business) são criados manualmente ou via data
    migration quando estiverem disponíveis.
    """
    Plan.objects.get_or_create(
        slug='free',
        defaults={
            'name': 'Free',
            'price': 0,
            'is_available': True,
            'max_users': 3,
            'max_clients': 50,
            'max_policies': 100,
            'features': [
                'Até 3 usuários',
                'Até 50 clientes',
                'Até 100 apólices',
                'Assistente IA básico',
            ],
        },
    )