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

from insurers.forms import InsurerForm
from insurers.models import Insurer
from shared.mixins import TenantMixin


class InsurerListView(LoginRequiredMixin, TenantMixin, ListView):
    model = Insurer
    template_name = 'insurers/insurer_list.html'
    context_object_name = 'insurers'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(name__icontains=q)
                | Q(cnpj__icontains=q)
                | Q(email__icontains=q)
            )
        return qs


class InsurerCreateView(LoginRequiredMixin, TenantMixin, CreateView):
    model = Insurer
    form_class = InsurerForm
    template_name = 'insurers/insurer_form.html'
    success_url = reverse_lazy('insurers:insurer_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Seguradora cadastrada com sucesso.')
        return response


class InsurerDetailView(LoginRequiredMixin, TenantMixin, DetailView):
    model = Insurer
    template_name = 'insurers/insurer_detail.html'
    context_object_name = 'insurer'


class InsurerUpdateView(LoginRequiredMixin, TenantMixin, UpdateView):
    model = Insurer
    form_class = InsurerForm
    template_name = 'insurers/insurer_form.html'
    success_url = reverse_lazy('insurers:insurer_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Seguradora atualizada com sucesso.')
        return response


class InsurerDeleteView(LoginRequiredMixin, TenantMixin, DeleteView):
    model = Insurer
    template_name = 'insurers/insurer_confirm_delete.html'
    success_url = reverse_lazy('insurers:insurer_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Seguradora excluida com sucesso.')
        return response
