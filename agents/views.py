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

from agents.forms import AgentForm, ProducerForm
from agents.models import Agent, Producer
from shared.mixins import TenantMixin


# ──────────────────────────────────────────────
# Agent views
# ──────────────────────────────────────────────

class AgentListView(LoginRequiredMixin, TenantMixin, ListView):
    model = Agent
    template_name = 'agents/agent_list.html'
    context_object_name = 'agents'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                Q(name__icontains=q) |
                Q(cpf_cnpj__icontains=q) |
                Q(email__icontains=q)
            )
        return qs


class AgentCreateView(LoginRequiredMixin, TenantMixin, CreateView):
    model = Agent
    form_class = AgentForm
    template_name = 'agents/agent_form.html'
    success_url = reverse_lazy('agents:agent_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Agente cadastrado com sucesso.')
        return response


class AgentDetailView(LoginRequiredMixin, TenantMixin, DetailView):
    model = Agent
    template_name = 'agents/agent_detail.html'
    context_object_name = 'agent'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['producers'] = self.object.producers.all()
        return context


class AgentUpdateView(LoginRequiredMixin, TenantMixin, UpdateView):
    model = Agent
    form_class = AgentForm
    template_name = 'agents/agent_form.html'
    success_url = reverse_lazy('agents:agent_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Agente atualizado com sucesso.')
        return response


class AgentDeleteView(LoginRequiredMixin, TenantMixin, DeleteView):
    model = Agent
    template_name = 'agents/agent_confirm_delete.html'
    success_url = reverse_lazy('agents:agent_list')

    def form_valid(self, form):
        messages.success(self.request, 'Agente excluído com sucesso.')
        return super().form_valid(form)


# ──────────────────────────────────────────────
# Producer views
# ──────────────────────────────────────────────

class ProducerListView(LoginRequiredMixin, TenantMixin, ListView):
    model = Producer
    template_name = 'producers/producer_list.html'
    context_object_name = 'producers'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related('agent')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                Q(name__icontains=q) |
                Q(cpf__icontains=q) |
                Q(email__icontains=q)
            )
        return qs


class ProducerCreateView(LoginRequiredMixin, TenantMixin, CreateView):
    model = Producer
    form_class = ProducerForm
    template_name = 'producers/producer_form.html'
    success_url = reverse_lazy('producers:producer_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.user.get_active_brokerage()
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Produtor cadastrado com sucesso.')
        return response


class ProducerDetailView(LoginRequiredMixin, TenantMixin, DetailView):
    model = Producer
    template_name = 'producers/producer_detail.html'
    context_object_name = 'producer'


class ProducerUpdateView(LoginRequiredMixin, TenantMixin, UpdateView):
    model = Producer
    form_class = ProducerForm
    template_name = 'producers/producer_form.html'
    success_url = reverse_lazy('producers:producer_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.user.get_active_brokerage()
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Produtor atualizado com sucesso.')
        return response


class ProducerDeleteView(LoginRequiredMixin, TenantMixin, DeleteView):
    model = Producer
    template_name = 'producers/producer_confirm_delete.html'
    success_url = reverse_lazy('producers:producer_list')

    def form_valid(self, form):
        messages.success(self.request, 'Produtor excluído com sucesso.')
        return super().form_valid(form)
