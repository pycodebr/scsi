from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from coverages.forms import CoverageTypeForm
from coverages.models import CoverageType
from shared.mixins import TenantMixin


class CoverageTypeListView(LoginRequiredMixin, TenantMixin, ListView):
    model = CoverageType
    template_name = 'coverages/coveragetype_list.html'
    context_object_name = 'coverage_types'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related('insurance_branch')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(Q(name__icontains=q))
        return qs


class CoverageTypeCreateView(LoginRequiredMixin, TenantMixin, CreateView):
    model = CoverageType
    form_class = CoverageTypeForm
    template_name = 'coverages/coveragetype_form.html'
    success_url = reverse_lazy('coverages:coveragetype_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.user.get_active_brokerage()
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Tipo de cobertura cadastrado com sucesso.')
        return response


class CoverageTypeDetailView(LoginRequiredMixin, TenantMixin, DetailView):
    model = CoverageType
    template_name = 'coverages/coveragetype_detail.html'
    context_object_name = 'coverage_type'


class CoverageTypeUpdateView(LoginRequiredMixin, TenantMixin, UpdateView):
    model = CoverageType
    form_class = CoverageTypeForm
    template_name = 'coverages/coveragetype_form.html'
    success_url = reverse_lazy('coverages:coveragetype_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.user.get_active_brokerage()
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Tipo de cobertura atualizado com sucesso.')
        return response


class CoverageTypeDeleteView(LoginRequiredMixin, TenantMixin, DeleteView):
    model = CoverageType
    template_name = 'coverages/coveragetype_confirm_delete.html'
    success_url = reverse_lazy('coverages:coveragetype_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Tipo de cobertura excluído com sucesso.')
        return response
