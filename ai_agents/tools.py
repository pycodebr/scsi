from langchain_core.tools import tool
from django.db.models import Q, Sum, Count


def _serialize_qs(qs, fields):
    rows = []
    for obj in qs:
        row = {}
        for f in fields:
            val = getattr(obj, f, None)
            if callable(val):
                val = val()
            if hasattr(val, 'isoformat'):
                val = val.isoformat()
            row[f] = val
        rows.append(row)
    return rows


def build_tenant_tools(brokerage):
    @tool
    def list_clients(query: str = '') -> str:
        """Lista clientes da corretora (filtra por nome/documento)."""
        from clients.models import Client
        qs = Client.objects.filter(brokerage=brokerage)
        if query:
            qs = qs.filter(Q(name__icontains=query) | Q(document__icontains=query))
        rows = _serialize_qs(qs[:20], ['id', 'name', 'person_type', 'document', 'email', 'phone', 'is_active'])
        import json
        return json.dumps(rows, ensure_ascii=False)

    @tool
    def get_client(client_id: int) -> str:
        """Retorna detalhes de um cliente da corretora."""
        from clients.models import Client
        try:
            c = Client.objects.filter(brokerage=brokerage, pk=client_id).first()
            if not c:
                return 'Cliente não encontrado.'
            import json
            data = {
                'id': c.id, 'name': c.name, 'person_type': c.person_type,
                'document': c.document, 'email': c.email, 'phone': c.phone,
                'is_active': c.is_active,
                'policies_count': c.policies.filter(brokerage=brokerage).count() if hasattr(c, 'policies') else 0,
            }
            return json.dumps(data, ensure_ascii=False, default=str)
        except Exception as e:
            return f'Erro: {e}'

    @tool
    def get_policy(policy_id: int) -> str:
        """Retorna detalhes de uma apólice da corretora."""
        from insurance.models import Policy
        try:
            p = Policy.objects.filter(brokerage=brokerage, pk=policy_id).select_related('client', 'insurer', 'line_of_business').first()
            if not p:
                return 'Apólice não encontrada.'
            import json
            data = {
                'id': p.id, 'policy_number': p.policy_number, 'status': p.status,
                'client_name': p.client.name if p.client_id else None,
                'insurer_name': p.insurer.name if p.insurer_id else None,
                'line_of_business': p.line_of_business.name if p.line_of_business_id else None,
                'premium': str(p.premium), 'start_date': str(p.start_date),
                'end_date': str(p.end_date),
            }
            return json.dumps(data, ensure_ascii=False, default=str)
        except Exception as e:
            return f'Erro: {e}'

    @tool
    def list_policies(status: str = '') -> str:
        """Lista apólices da corretora, opcionalmente filtrando por status."""
        from insurance.models import Policy
        qs = Policy.objects.filter(brokerage=brokerage).select_related('client', 'insurer')
        if status:
            qs = qs.filter(status=status)
        rows = _serialize_qs(qs[:20], ['id', 'policy_number', 'status', 'premium', 'start_date', 'end_date'])
        import json
        return json.dumps(rows, ensure_ascii=False, default=str)

    @tool
    def get_proposal(proposal_id: int) -> str:
        """Retorna detalhes de uma proposta da corretora."""
        from insurance.models import Proposal
        try:
            p = Proposal.objects.filter(brokerage=brokerage, pk=proposal_id).select_related('client', 'insurer', 'line_of_business').first()
            if not p:
                return 'Proposta não encontrada.'
            import json
            data = {
                'id': p.id, 'status': p.status,
                'client_name': p.client.name if p.client_id else None,
                'insurer_name': p.insurer.name if p.insurer_id else None,
                'line_of_business': p.line_of_business.name if p.line_of_business_id else None,
                'premium': str(p.premium), 'created_at': str(p.created_at),
            }
            return json.dumps(data, ensure_ascii=False, default=str)
        except Exception as e:
            return f'Erro: {e}'

    @tool
    def get_claim(claim_id: int) -> str:
        """Retorna detalhes de um sinistro da corretora."""
        from claims.models import Claim
        try:
            c = Claim.objects.filter(brokerage=brokerage, pk=claim_id).select_related('policy', 'covered_item').first()
            if not c:
                return 'Sinistro não encontrado.'
            import json
            data = {
                'id': c.id, 'claim_number': c.claim_number, 'status': c.status,
                'policy_number': c.policy.policy_number if c.policy_id else None,
                'occurrence_date': str(c.occurrence_date),
                'claimed_amount': str(c.claimed_amount),
                'approved_amount': str(c.approved_amount),
            }
            return json.dumps(data, ensure_ascii=False, default=str)
        except Exception as e:
            return f'Erro: {e}'

    @tool
    def list_claims(status: str = '') -> str:
        """Lista sinistros da corretora, opcionalmente filtrando por status."""
        from claims.models import Claim
        qs = Claim.objects.filter(brokerage=brokerage).select_related('policy')
        if status:
            qs = qs.filter(status=status)
        rows = _serialize_qs(qs[:20], ['id', 'claim_number', 'status', 'claimed_amount', 'occurrence_date'])
        import json
        return json.dumps(rows, ensure_ascii=False, default=str)

    @tool
    def get_deal(deal_id: int) -> str:
        """Retorna detalhes de uma negociação do CRM da corretora."""
        from crm.models import Deal
        try:
            d = Deal.objects.filter(brokerage=brokerage, pk=deal_id).select_related('client', 'stage', 'pipeline').first()
            if not d:
                return 'Negociação não encontrada.'
            import json
            data = {
                'id': d.id, 'title': d.title, 'status': d.status,
                'stage': d.stage.name if d.stage_id else None,
                'estimated_value': str(d.estimated_value),
                'client_name': d.client.name if d.client_id else None,
            }
            return json.dumps(data, ensure_ascii=False, default=str)
        except Exception as e:
            return f'Erro: {e}'

    @tool
    def list_renewals_due(days: int = 30) -> str:
        """Lista apólices vencendo nos próximos N dias."""
        from insurance.models import Policy
        from datetime import date, timedelta
        threshold = date.today() + timedelta(days=days)
        qs = Policy.objects.filter(
            brokerage=brokerage,
            status='active',
            end_date__lte=threshold,
            end_date__gte=date.today(),
        ).select_related('client', 'insurer')[:20]
        rows = _serialize_qs(qs, ['id', 'policy_number', 'end_date', 'premium'])
        import json
        return json.dumps(rows, ensure_ascii=False, default=str)

    @tool
    def commissions_summary() -> str:
        """Retorna resumo de comissões da corretora."""
        from commissions.models import Commission
        from django.db.models import Sum
        qs = Commission.objects.filter(brokerage=brokerage)
        data = {
            'total_received': str(qs.filter(status='received').aggregate(s=Sum('amount'))['s'] or 0),
            'total_pending': str(qs.filter(status='pending').aggregate(s=Sum('amount'))['s'] or 0),
            'total': str(qs.aggregate(s=Sum('amount'))['s'] or 0),
        }
        import json
        return json.dumps(data, ensure_ascii=False)

    @tool
    def search_insurers(query: str = '') -> str:
        """Lista seguradoras da corretora, filtrando por nome."""
        from insurers.models import Insurer
        qs = Insurer.objects.filter(brokerage=brokerage, is_active=True)
        if query:
            qs = qs.filter(Q(name__icontains=query))
        rows = _serialize_qs(qs[:20], ['id', 'name', 'cnpj', 'susep_code'])
        import json
        return json.dumps(rows, ensure_ascii=False, default=str)

    return [
        list_clients, get_client, get_policy, list_policies,
        get_proposal, get_claim, list_claims, get_deal,
        list_renewals_due, commissions_summary, search_insurers,
    ]