from decimal import Decimal
from .models import Commission, CommissionSplit


def create_commission_from_policy(policy):
    """Create a Commission + CommissionSplits when a Policy is created.

    Called from `generate_policy_from_proposal` or a post_save signal.
    Uses policy.commission_rate, the policy's agent/producer default rates,
    and the proposal's producer/agent FKs to build splits.
    """
    brokerage = policy.brokerage
    insurer_amount = policy.total_premium * (policy.commission_rate / Decimal('100'))
    commission = Commission.objects.create(
        brokerage=brokerage,
        policy=policy,
        base_premium=policy.net_premium,
        insurer_rate=policy.commission_rate,
        insurer_amount=insurer_amount,
        reference_date=policy.start_date,
        status=Commission.Status.PENDING,
    )

    # Create splits for agent and/or producer if linked
    total_split_rate = Decimal('0')

    if policy.agent:
        rate = policy.agent.default_commission_rate or Decimal('0')
        amount = insurer_amount * (rate / Decimal('100'))
        CommissionSplit.objects.create(
            brokerage=brokerage,
            commission=commission,
            beneficiary_type=CommissionSplit.BeneficiaryType.AGENT,
            agent=policy.agent,
            rate=rate,
            amount=amount,
            status=CommissionSplit.SplitStatus.PENDING,
        )
        total_split_rate += rate

    producer = None
    # Polity has no direct producer FK yet; check proposal if available
    if hasattr(policy, 'proposal') and policy.proposal and policy.proposal.producer:
        producer = policy.proposal.producer
    elif hasattr(policy, 'producer') and policy.producer:
        producer = policy.producer

    if producer:
        rate = producer.default_commission_rate or Decimal('0')
        amount = insurer_amount * (rate / Decimal('100'))
        CommissionSplit.objects.create(
            brokerage=brokerage,
            commission=commission,
            beneficiary_type=CommissionSplit.BeneficiaryType.PRODUCER,
            producer=producer,
            rate=rate,
            amount=amount,
            status=CommissionSplit.SplitStatus.PENDING,
        )
        total_split_rate += rate

    return commission