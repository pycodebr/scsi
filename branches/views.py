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

from branches.forms import InsuranceBranchForm
from branches.models import InsuranceBranch
from shared.mixins import TenantMixin


class InsuranceBranchListView(LoginRequiredMixin, TenantMixin, ListView):
    model = InsuranceBranch
    template_name = 'branches/branch_list.html'
    context_object_name = 'branches'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(name__icontains=q)
                | Q(code__icontains=q)
            )
        return qs


class InsuranceBranchCreateView(LoginRequiredMixin, TenantMixin, CreateView):
    model = InsuranceBranch
    form_class = InsuranceBranchForm
    template_name = 'branches/branch_form.html'
    success_url = reverse_lazy('branches:branch_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Ramo de seguro cadastrado com sucesso.')
        return response


class InsuranceBranchDetailView(LoginRequiredMixin, TenantMixin, DetailView):
    model = InsuranceBranch
    template_name = 'branches/branch_detail.html'
    context_object_name = 'branch'


class InsuranceBranchUpdateView(LoginRequiredMixin, TenantMixin, UpdateView):
    model = InsuranceBranch
    form_class = InsuranceBranchForm
    template_name = 'branches/branch_form.html'
    success_url = reverse_lazy('branches:branch_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Ramo de seguro atualizado com sucesso.')
        return response


class InsuranceBranchDeleteView(LoginRequiredMixin, TenantMixin, DeleteView):
    model = InsuranceBranch
    template_name = 'branches/branch_confirm_delete.html'
    success_url = reverse_lazy('branches:branch_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Ramo de seguro excluído com sucesso.')
        return response
