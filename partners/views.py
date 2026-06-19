from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView

from base.mixins import PerPageMixin, RoleRequiredMixin, TenantQuerysetMixin
from .models import Agent, Producer
from .forms import AgentForm, ProducerForm


class AgentListView(PerPageMixin, RoleRequiredMixin, TenantQuerysetMixin, ListView):
    allowed_roles = ('owner', 'manager', 'broker', 'operational')
    model = Agent
    template_name = 'partners/agent_list.html'
    context_object_name = 'agents'
    paginate_by = 10
    per_page_query_params = ('q',)

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q', '')
        if q:
            qs = qs.filter(name__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_q'] = self.request.GET.get('q', '')
        return ctx


class AgentCreateView(RoleRequiredMixin, TenantQuerysetMixin, CreateView):
    allowed_roles = ('owner', 'manager')
    model = Agent
    form_class = AgentForm
    template_name = 'partners/agent_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.brokerage = self.request.tenant
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('partners:agent_detail', kwargs={'pk': self.object.pk})


class AgentUpdateView(RoleRequiredMixin, TenantQuerysetMixin, UpdateView):
    allowed_roles = ('owner', 'manager')
    model = Agent
    form_class = AgentForm
    template_name = 'partners/agent_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_success_url(self):
        return reverse_lazy('partners:agent_detail', kwargs={'pk': self.object.pk})


class AgentDetailView(RoleRequiredMixin, TenantQuerysetMixin, DetailView):
    allowed_roles = ('owner', 'manager', 'broker', 'operational')
    model = Agent
    template_name = 'partners/agent_detail.html'
    context_object_name = 'agent'

    def get_queryset(self):
        return super().get_queryset().select_related('user').prefetch_related('producers')


class ProducerListView(PerPageMixin, RoleRequiredMixin, TenantQuerysetMixin, ListView):
    allowed_roles = ('owner', 'manager', 'broker', 'operational')
    model = Producer
    template_name = 'partners/producer_list.html'
    context_object_name = 'producers'
    paginate_by = 10
    per_page_query_params = ('q',)

    def get_queryset(self):
        qs = super().get_queryset().select_related('agent')
        q = self.request.GET.get('q', '')
        if q:
            qs = qs.filter(name__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_q'] = self.request.GET.get('q', '')
        return ctx


class ProducerCreateView(RoleRequiredMixin, TenantQuerysetMixin, CreateView):
    allowed_roles = ('owner', 'manager')
    model = Producer
    form_class = ProducerForm
    template_name = 'partners/producer_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.brokerage = self.request.tenant
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('partners:producer_detail', kwargs={'pk': self.object.pk})


class ProducerUpdateView(RoleRequiredMixin, TenantQuerysetMixin, UpdateView):
    allowed_roles = ('owner', 'manager')
    model = Producer
    form_class = ProducerForm
    template_name = 'partners/producer_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def get_success_url(self):
        return reverse_lazy('partners:producer_detail', kwargs={'pk': self.object.pk})


class ProducerDetailView(RoleRequiredMixin, TenantQuerysetMixin, DetailView):
    allowed_roles = ('owner', 'manager', 'broker', 'operational')
    model = Producer
    template_name = 'partners/producer_detail.html'
    context_object_name = 'producer'

    def get_queryset(self):
        return super().get_queryset().select_related('agent', 'user')