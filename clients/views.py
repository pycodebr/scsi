from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from base.mixins import PerPageMixin, RoleRequiredMixin, TenantQuerysetMixin
from documents.models import Document
from .forms import ClientForm, ClientSearchForm
from .models import Client


class ClientListView(PerPageMixin, RoleRequiredMixin, TenantQuerysetMixin, ListView):
    allowed_roles = ('owner', 'manager', 'broker', 'agent', 'producer', 'operational')
    model = Client
    template_name = 'clients/client_list.html'
    context_object_name = 'clients'
    paginate_by = 10
    per_page_query_params = ('q', 'person_type')

    def get_queryset(self):
        qs = super().get_queryset()
        form = ClientSearchForm(self.request.GET)
        if form.is_valid():
            q = form.cleaned_data.get('q')
            person_type = form.cleaned_data.get('person_type')
            if q:
                qs = qs.filter(
                    Q(name__icontains=q) | Q(document__icontains=q) | Q(email__icontains=q)
                )
            if person_type:
                qs = qs.filter(person_type=person_type)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_form'] = ClientSearchForm(self.request.GET)
        return ctx


class ClientCreateView(RoleRequiredMixin, CreateView):
    """Cria cliente dentro do tenant."""

    allowed_roles = ('owner', 'manager', 'broker', 'agent', 'producer')
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('clients:client_list')

    def form_valid(self, form):
        form.instance.brokerage = self.request.tenant
        messages.success(self.request, f'Cliente "{form.instance.name}" criado com sucesso.')
        return super().form_valid(form)


class ClientUpdateView(RoleRequiredMixin, UpdateView):
    """Atualiza cliente dentro do tenant."""

    allowed_roles = ('owner', 'manager', 'broker', 'agent')
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('clients:client_list')

    def get_queryset(self):
        return Client.objects.filter(brokerage=self.request.tenant)

    def form_valid(self, form):
        messages.success(self.request, f'Cliente "{form.instance.name}" atualizado.')
        return super().form_valid(form)


class ClientDetailView(RoleRequiredMixin, TenantQuerysetMixin, DetailView):
    """Detalhe do cliente com abas (apólices, propostas, sinistros, anexos)."""

    allowed_roles = ('owner', 'manager', 'broker', 'agent', 'producer', 'operational')
    model = Client
    template_name = 'clients/client_detail.html'
    context_object_name = 'client'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        client = self.object
        client_ct = ContentType.objects.get_for_model(Client)
        ctx['content_type_id'] = client_ct.pk
        ctx['documents'] = Document.objects.filter(
            content_type_id=client_ct.pk,
            object_id=client.pk,
            brokerage=self.request.tenant,
        ).order_by('-created_at')

        tab = self.request.GET.get('tab', 'info')
        ctx['active_tab'] = tab
        return ctx