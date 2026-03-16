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

from clients.forms import ClientForm
from clients.models import Client
from shared.mixins import TenantMixin


class ClientListView(LoginRequiredMixin, TenantMixin, ListView):
    model = Client
    template_name = 'clients/client_list.html'
    context_object_name = 'clients'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related('assigned_producer')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(name__icontains=q)
                | Q(cpf_cnpj__icontains=q)
                | Q(email__icontains=q)
            )
        return qs


class ClientCreateView(LoginRequiredMixin, TenantMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('clients:client_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.user.get_active_brokerage()
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Cliente cadastrado com sucesso.')
        return response


class ClientDetailView(LoginRequiredMixin, TenantMixin, DetailView):
    model = Client
    template_name = 'clients/client_detail.html'
    context_object_name = 'client'


class ClientUpdateView(LoginRequiredMixin, TenantMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('clients:client_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.user.get_active_brokerage()
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Cliente atualizado com sucesso.')
        return response


class ClientDeleteView(LoginRequiredMixin, TenantMixin, DeleteView):
    model = Client
    template_name = 'clients/client_confirm_delete.html'
    success_url = reverse_lazy('clients:client_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Cliente excluído com sucesso.')
        return response
