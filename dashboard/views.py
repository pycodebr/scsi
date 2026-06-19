import json
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncMonth
from datetime import date, timedelta

from django.views.generic import TemplateView

from base.mixins import RoleRequiredMixin


class DashboardView(RoleRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'
    allowed_roles = ('owner', 'manager', 'broker', 'agent', 'producer', 'operational')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        brokerage = self.request.tenant
        today = date.today()
        period_start = self._get_period_start()

        from clients.models import Client
        from insurance.models import Policy, Proposal, Renewal
        from claims.models import Claim
        from commissions.models import Commission
        from crm.models import Deal, Stage, Pipeline

        active_policies = Policy.objects.filter(brokerage=brokerage, status='active')
        policies_count = active_policies.count()
        total_premium = active_policies.aggregate(t=Sum('total_premium'))['t'] or 0

        total_clients = Client.objects.filter(brokerage=brokerage, is_active=True).count()
        new_clients_period = Client.objects.filter(
            brokerage=brokerage, created_at__date__gte=period_start,
        ).count()

        open_proposals = Proposal.objects.filter(
            brokerage=brokerage, status__in=('draft', 'sent', 'under_analysis')
        ).count()
        open_proposals_value = Proposal.objects.filter(
            brokerage=brokerage, status__in=('draft', 'sent', 'under_analysis')
        ).aggregate(t=Sum('total_premium'))['t'] or 0

        open_claims = Claim.objects.filter(
            brokerage=brokerage, status__in=('opened', 'under_analysis')
        ).count()
        open_claims_value = Claim.objects.filter(
            brokerage=brokerage, status__in=('opened', 'under_analysis')
        ).aggregate(t=Sum('claimed_amount'))['t'] or 0

        renewals_due = Renewal.objects.filter(
            brokerage=brokerage, status='pending',
            due_date__lte=today + timedelta(days=30),
        ).count()
        renewals_premium_at_risk = Renewal.objects.filter(
            brokerage=brokerage, status='pending',
            due_date__lte=today + timedelta(days=30),
        ).aggregate(t=Sum('policy__total_premium'))['t'] or 0

        active_deals = Deal.objects.filter(brokerage=brokerage, status='open').count()
        won_deals = Deal.objects.filter(brokerage=brokerage, status='won')
        won_count = won_deals.count()
        won_value = won_deals.aggregate(t=Sum('estimated_value'))['t'] or 0
        lost_deals = Deal.objects.filter(brokerage=brokerage, status='lost')
        lost_count = lost_deals.count()
        lost_value = lost_deals.aggregate(t=Sum('estimated_value'))['t'] or 0
        total_deals = won_count + lost_count + active_deals
        conversion_rate = round((won_count / total_deals) * 100, 1) if total_deals > 0 else 0

        commission_pending = Commission.objects.filter(
            brokerage=brokerage, status='pending'
        ).aggregate(t=Sum('insurer_amount'))['t'] or 0
        commission_pending_count = Commission.objects.filter(
            brokerage=brokerage, status='pending'
        ).count()

        avg_premium = total_premium / policies_count if policies_count > 0 else 0

        claims_total_count = Claim.objects.filter(brokerage=brokerage).count()
        claims_total_value = Claim.objects.filter(brokerage=brokerage).aggregate(
            t=Sum('claimed_amount')
        )['t'] or 0
        claims_paid_value = Claim.objects.filter(
            brokerage=brokerage, status='paid'
        ).aggregate(t=Sum('approved_amount'))['t'] or 0
        claims_approval_rate = round(
            (Claim.objects.filter(brokerage=brokerage, status__in=('approved', 'paid')).count() / claims_total_count) * 100, 1
        ) if claims_total_count > 0 else 0

        policies_expiring_90 = Policy.objects.filter(
            brokerage=brokerage, status='active',
            end_date__lte=today + timedelta(days=90),
        ).count()

        won_deals_period = Deal.objects.filter(
            brokerage=brokerage, status='won', created_at__date__gte=period_start,
        ).aggregate(t=Sum('estimated_value'))['t'] or 0

        recent_policies = list(Policy.objects.filter(
            brokerage=brokerage
        ).select_related('client', 'insurer').order_by('-created_at')[:5])

        upcoming_renewals = list(Renewal.objects.filter(
            brokerage=brokerage, status='pending',
            due_date__lte=today + timedelta(days=90),
        ).select_related('policy', 'policy__client').order_by('due_date')[:5])

        ctx.update({
            'total_clients': total_clients,
            'new_clients_period': new_clients_period,
            'active_policies': policies_count,
            'total_premium': total_premium,
            'open_proposals': open_proposals,
            'open_proposals_value': open_proposals_value,
            'open_claims': open_claims,
            'open_claims_value': open_claims_value,
            'renewals_due_30d': renewals_due,
            'renewals_premium_at_risk': renewals_premium_at_risk,
            'total_commission_pending': commission_pending,
            'commission_pending_count': commission_pending_count,
            'avg_premium': avg_premium,
            'claims_total_count': claims_total_count,
            'claims_total_value': claims_total_value,
            'claims_paid_value': claims_paid_value,
            'claims_approval_rate': claims_approval_rate,
            'policies_expiring_90': policies_expiring_90,
            'won_deals_value_period': won_deals_period,
            'active_deals': active_deals,
            'won_deals_count': won_count,
            'won_deals_value': won_value,
            'lost_deals_count': lost_count,
            'lost_deals_value': lost_value,
            'conversion_rate': conversion_rate,
            'recent_policies': recent_policies,
            'upcoming_renewals': upcoming_renewals,
        })

        pipeline = Pipeline.objects.filter(brokerage=brokerage, is_default=True).first()
        if not pipeline:
            pipeline = Pipeline.objects.filter(brokerage=brokerage).first()

        funnel_labels, funnel_values, funnel_amounts, funnel_colors = [], [], [], []
        if pipeline:
            stages = Stage.objects.filter(pipeline=pipeline).order_by('order')
            funnel_data = []
            max_count = 0
            for stage in stages:
                count = Deal.objects.filter(brokerage=brokerage, stage=stage).count()
                value = Deal.objects.filter(brokerage=brokerage, stage=stage).aggregate(
                    t=Sum('estimated_value')
                )['t'] or 0
                if count > max_count:
                    max_count = count
                funnel_data.append({
                    'name': stage.name, 'color': stage.color,
                    'is_won': stage.is_won, 'is_lost': stage.is_lost,
                    'count': count, 'value': value, 'pct': 0,
                })
                funnel_labels.append(stage.name)
                funnel_values.append(count)
                funnel_amounts.append(float(value))
                funnel_colors.append(stage.color)
            for idx, item in enumerate(funnel_data):
                item['pct'] = int((item['count'] / max_count) * 100) if max_count > 0 else 0
            ctx['funnel_data'] = funnel_data
        else:
            ctx['funnel_data'] = []

        ctx['funnel_labels'] = json.dumps(funnel_labels)
        ctx['funnel_values'] = json.dumps(funnel_values)
        ctx['funnel_amounts'] = json.dumps(funnel_amounts)
        ctx['funnel_colors'] = json.dumps(funnel_colors)

        policies_by_lob = list(Policy.objects.filter(
            brokerage=brokerage, status='active'
        ).values('line_of_business__name').annotate(
            count=Count('id'), total_premium=Sum('total_premium')
        ).order_by('-count'))
        ctx['chart_lob_labels'] = json.dumps([i['line_of_business__name'] or 'Sem ramo' for i in policies_by_lob])
        ctx['chart_lob_values'] = json.dumps([i['count'] for i in policies_by_lob])

        claims_by_status = list(Claim.objects.filter(
            brokerage=brokerage
        ).values('status').annotate(count=Count('id'), total=Sum('claimed_amount')).order_by('-count'))
        status_map = {
            'opened': 'Aberto', 'under_analysis': 'Em Análise',
            'approved': 'Aprovado', 'paid': 'Pago', 'closed': 'Fechado',
        }
        ctx['chart_claims_labels'] = json.dumps([status_map.get(i['status'], i['status']) for i in claims_by_status])
        ctx['chart_claims_values'] = json.dumps([i['count'] for i in claims_by_status])

        top_insurers = list(Policy.objects.filter(
            brokerage=brokerage, status='active'
        ).values('insurer__name').annotate(
            count=Count('id'), total_premium=Sum('total_premium')
        ).order_by('-total_premium')[:5])
        ctx['chart_insurer_labels'] = json.dumps([i['insurer__name'] or 'N/A' for i in top_insurers])
        ctx['chart_insurer_values'] = json.dumps([i['count'] for i in top_insurers])

        monthly_premium = list(Policy.objects.filter(
            brokerage=brokerage, created_at__date__gte=period_start,
        ).annotate(month=TruncMonth('created_at')).values('month').annotate(
            total=Sum('total_premium')
        ).order_by('month'))

        monthly_commission = list(Commission.objects.filter(
            brokerage=brokerage, created_at__date__gte=period_start,
        ).annotate(month=TruncMonth('created_at')).values('month').annotate(
            total=Sum('insurer_amount')
        ).order_by('month'))

        all_months = sorted(set(
            [e['month'].strftime('%b/%Y') for e in monthly_premium if e['month']] +
            [e['month'].strftime('%b/%Y') for e in monthly_commission if e['month']]
        ))
        premium_map = {e['month'].strftime('%b/%Y'): float(e['total'] or 0) for e in monthly_premium if e['month']}
        commission_map = {e['month'].strftime('%b/%Y'): float(e['total'] or 0) for e in monthly_commission if e['month']}

        ctx['chart_months'] = json.dumps(all_months)
        ctx['chart_premiums'] = json.dumps([premium_map.get(m, 0) for m in all_months])
        ctx['chart_commissions'] = json.dumps([commission_map.get(m, 0) for m in all_months])

        ctx['period_start'] = period_start
        ctx['period_end'] = today
        return ctx

    def _get_period_start(self):
        period = self.request.GET.get('period', '30')
        today = date.today()
        if period == '7':
            return today - timedelta(days=7)
        elif period == '90':
            return today - timedelta(days=90)
        elif period == '365':
            return today - timedelta(days=365)
        return today - timedelta(days=30)