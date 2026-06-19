import logging
from django.utils import timezone

from celery import shared_task

logger = logging.getLogger(__name__)

ENTITY_MODEL_MAP = {
    'client': ('clients.models', 'Client'),
    'policy': ('insurance.models', 'Policy'),
    'proposal': ('insurance.models', 'Proposal'),
    'claim': ('claims.models', 'Claim'),
    'deal': ('crm.models', 'Deal'),
}

SUMMARY_URL_MAP = {
    'client': '/clientes/{pk}/',
    'policy': '/insurance/apolices/{pk}/',
    'proposal': '/insurance/propostas/{pk}/',
    'claim': '/sinistros/{pk}/',
    'deal': '/crm/negociacoes/{pk}/',
}


def _get_model(entity_type):
    import importlib
    module_path, model_name = ENTITY_MODEL_MAP[entity_type]
    module = importlib.import_module(module_path)
    return getattr(module, model_name)


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def generate_summary(self, entity_type, entity_id):
    """Celery task que gera resumo IA para uma entidade e notifica o usuário."""
    import importlib
    from django.contrib.auth import get_user_model
    from notifications.models import Notification

    Model = _get_model(entity_type)

    try:
        obj = Model.objects.select_related('brokerage').get(pk=entity_id)
    except Model.DoesNotExist:
        logger.error('%s #%s não encontrado.', entity_type, entity_id)
        return f'{entity_type} #{entity_id} não encontrado.'

    brokerage = obj.brokerage

    obj.ai_summary_status = 'processing'
    Model.objects.filter(pk=entity_id).update(ai_summary_status='processing')

    try:
        from ai_agents.agents import run_summary_agent
        summary = run_summary_agent(entity_type, entity_id, brokerage)
    except Exception as exc:
        Model.objects.filter(pk=entity_id).update(ai_summary_status='error')
        logger.exception('Erro ao gerar resumo para %s #%s', entity_type, entity_id)

        User = get_user_model()
        users = User.objects.filter(
            brokerage=brokerage,
            is_active=True,
            role__in=('owner', 'manager'),
        )
        url = SUMMARY_URL_MAP.get(entity_type, '/').format(pk=entity_id)
        for user in users:
            Notification.objects.create(
                brokerage=brokerage,
                user=user,
                type=Notification.Type.AI_SUMMARY,
                title=f'Erro ao gerar resumo de {entity_type}',
                message=f'Não foi possível gerar o resumo IA para {entity_type} #{entity_id}. Tente novamente.',
                url=url,
            )

        raise self.retry(exc=exc)

    Model.objects.filter(pk=entity_id).update(
        ai_summary=summary,
        ai_summary_status='done',
        ai_summary_updated_at=timezone.now(),
    )

    User = get_user_model()
    users = User.objects.filter(
        brokerage=brokerage,
        is_active=True,
        role__in=('owner', 'manager'),
    )
    url = SUMMARY_URL_MAP.get(entity_type, '/').format(pk=entity_id)
    entity_display = getattr(obj, 'name', getattr(obj, 'policy_number', getattr(obj, 'title', f'#{entity_id}')))
    for user in users:
        Notification.objects.create(
            brokerage=brokerage,
            user=user,
            type=Notification.Type.AI_SUMMARY,
            title=f'Resumo IA pronto: {entity_display}',
            message=f'O resumo IA para {entity_type} "{entity_display}" foi gerado com sucesso.',
            url=url,
        )

    return f'Summary generated for {entity_type} #{entity_id}'


@shared_task
def generate_client_summary(client_id):
    return generate_summary('client', client_id)


@shared_task
def generate_policy_summary(policy_id):
    return generate_summary('policy', policy_id)


@shared_task
def generate_proposal_summary(proposal_id):
    return generate_summary('proposal', proposal_id)


@shared_task
def generate_claim_summary(claim_id):
    return generate_summary('claim', claim_id)


@shared_task
def generate_deal_summary(deal_id):
    return generate_summary('deal', deal_id)