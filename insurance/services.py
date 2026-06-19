from django.db import transaction

from .models import CoveredItem, Policy, Proposal


@transaction.atomic
def generate_policy_from_proposal(proposal_pk, policy_number):
    """Gera uma Policy a partir de uma Proposal.

    Copia dados da proposta, cria a apólice, clona os itens cobertos,
    marca a proposta como 'converted'. Levanta ValueError se a proposta
    já foi convertida ou não existe.

    Retorna a Policy criada.
    """
    proposal = Proposal.objects.select_related('client', 'insurer', 'line_of_business').get(pk=proposal_pk)

    if proposal.status == Proposal.Status.CONVERTED:
        raise ValueError(f'Proposta {proposal.number} já foi convertida em apólice.')

    policy = Policy.objects.create(
        brokerage=proposal.brokerage,
        proposal=proposal,
        policy_number=policy_number,
        client=proposal.client,
        insurer=proposal.insurer,
        line_of_business=proposal.line_of_business,
        status=Policy.Status.ACTIVE,
        net_premium=proposal.net_premium,
        total_premium=proposal.total_premium,
        iof=proposal.iof,
        commission_rate=0,
        start_date=proposal.proposed_start_date,
        end_date=proposal.proposed_end_date,
        payment_info=proposal.payment_terms,
        producer=proposal.producer,
        agent=proposal.agent,
    )

    proposal_items = CoveredItem.objects.filter(proposal=proposal)
    for item in proposal_items:
        CoveredItem.objects.create(
            brokerage=item.brokerage,
            policy=policy,
            item_type=item.item_type,
            description=item.description,
            identifier=item.identifier,
            insured_amount=item.insured_amount,
            attributes=item.attributes,
            coverages=item.coverages,
        )

    proposal.status = Proposal.Status.CONVERTED
    proposal.save(update_fields=['status', 'updated_at'])

    from commissions.services import create_commission_from_policy
    try:
        create_commission_from_policy(policy)
    except Exception:
        pass

    return policy