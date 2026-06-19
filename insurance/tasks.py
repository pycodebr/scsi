from datetime import date, timedelta

from celery import shared_task
from django.utils import timezone


@shared_task
def check_renewals_due():
    """Cria/atualiza renovações para apólices com vencimento próximo (30 dias)."""
    from insurance.models import Policy, Renewal
    from notifications.models import Notification

    threshold = date.today() + timedelta(days=30)
    policies = Policy.objects.filter(
        end_date__lte=threshold,
        end_date__gte=date.today(),
        status=Policy.Status.ACTIVE,
    ).select_related('brokerage')

    created_count = 0
    for policy in policies:
        renewal, created = Renewal.objects.get_or_create(
            policy=policy,
            brokerage=policy.brokerage,
            defaults={
                'status': Renewal.Status.PENDING,
                'due_date': policy.end_date,
            },
        )
        if created:
            created_count += 1
            # Notify brokerage users
            from accounts.models import User
            users = User.objects.filter(
                brokerage=policy.brokerage,
                is_active=True,
                role__in=('owner', 'manager', 'broker'),
            )
            for user in users:
                Notification.objects.create(
                    brokerage=policy.brokerage,
                    user=user,
                    type=Notification.Type.RENEWAL,
                    title=f'Apólice {policy.policy_number} vence em {policy.end_date.strftime("%d/%m/%Y")}',
                    message=f'A apólice {policy.policy_number} vence em breve. Verifique a renovação.',
                    url=f'/insurance/apolices/{policy.pk}/',
                )

    return f'Created {created_count} renewals'


@shared_task
def expire_policies():
    """Marca apólices com end_date passada como expired."""
    from insurance.models import Policy

    today = date.today()
    expired = Policy.objects.filter(
        end_date__lt=today,
        status=Policy.Status.ACTIVE,
    ).update(status=Policy.Status.EXPIRED)

    return f'Expired {expired} policies'