from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView

from base.mixins import PerPageMixin, RoleRequiredMixin, TenantQuerysetMixin
from .models import Commission
from .forms import CommissionSearchForm


class CommissionListView(PerPageMixin, RoleRequiredMixin, TenantQuerysetMixin, ListView):
    allowed_roles = ('owner', 'manager', 'broker', 'agent', 'producer', 'operational')
    model = Commission
    template_name = 'commissions/commission_list.html'
    context_object_name = 'commissions'
    paginate_by = 10
    per_page_query_params = ('status',)

    def get_queryset(self):
        qs = super().get_queryset().select_related('policy')
        params = self.request.GET
        if params.get('status'):
            qs = qs.filter(status=params['status'])
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_form'] = CommissionSearchForm(self.request.GET or None)
        return ctx


class CommissionDetailView(RoleRequiredMixin, TenantQuerysetMixin, DetailView):
    allowed_roles = ('owner', 'manager', 'broker', 'agent', 'producer', 'operational')
    model = Commission
    template_name = 'commissions/commission_detail.html'
    context_object_name = 'commission'

    def get_queryset(self):
        return super().get_queryset().select_related('policy', 'policy__client', 'policy__insurer')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['splits'] = self.object.splits.select_related('agent', 'producer')
        return ctx