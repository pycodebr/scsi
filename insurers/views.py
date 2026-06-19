from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from base.mixins import PerPageMixin, RoleRequiredMixin, TenantQuerysetMixin
from .forms import InsurerForm, LineOfBusinessForm
from .models import Insurer, LineOfBusiness


# ── Seguradoras ──────────────────────────────────────────────────────────────

class InsurerListView(PerPageMixin, RoleRequiredMixin, TenantQuerysetMixin, ListView):
    allowed_roles = ('owner', 'manager', 'broker', 'agent', 'producer', 'operational')
    model = Insurer
    template_name = 'insurers/insurer_list.html'
    context_object_name = 'insurers'
    paginate_by = 10
    per_page_query_params = ('q', 'is_active')

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(cnpj__icontains=q))
        status = self.request.GET.get('is_active')
        if status in ('1', '0'):
            qs = qs.filter(is_active=status == '1')
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        ctx['is_active'] = self.request.GET.get('is_active', '')
        return ctx


class InsurerCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = ('owner', 'manager', 'broker')
    model = Insurer
    form_class = InsurerForm
    template_name = 'insurers/insurer_form.html'
    success_url = reverse_lazy('insurers:insurer_list')

    def form_valid(self, form):
        form.instance.brokerage = self.request.tenant
        messages.success(self.request, f'Seguradora "{form.instance.name}" criada com sucesso.')
        return super().form_valid(form)


class InsurerUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = ('owner', 'manager', 'broker')
    model = Insurer
    form_class = InsurerForm
    template_name = 'insurers/insurer_form.html'
    success_url = reverse_lazy('insurers:insurer_list')

    def get_queryset(self):
        return Insurer.objects.filter(brokerage=self.request.tenant)

    def form_valid(self, form):
        messages.success(self.request, f'Seguradora "{form.instance.name}" atualizada.')
        return super().form_valid(form)


# ── Ramos ────────────────────────────────────────────────────────────────────

class LineOfBusinessListView(PerPageMixin, RoleRequiredMixin, TenantQuerysetMixin, ListView):
    allowed_roles = ('owner', 'manager', 'broker', 'agent', 'producer', 'operational')
    model = LineOfBusiness
    template_name = 'insurers/lob_list.html'
    context_object_name = 'lobs'
    paginate_by = 10
    per_page_query_params = ('q', 'category', 'is_active')

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(code__icontains=q))
        category = self.request.GET.get('category')
        if category:
            qs = qs.filter(category=category)
        status = self.request.GET.get('is_active')
        if status in ('1', '0'):
            qs = qs.filter(is_active=status == '1')
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        ctx['category'] = self.request.GET.get('category', '')
        ctx['is_active'] = self.request.GET.get('is_active', '')
        ctx['categories'] = LineOfBusiness.Category.choices
        return ctx


class LineOfBusinessCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = ('owner', 'manager', 'broker')
    model = LineOfBusiness
    form_class = LineOfBusinessForm
    template_name = 'insurers/lob_form.html'
    success_url = reverse_lazy('insurers:lob_list')

    def form_valid(self, form):
        form.instance.brokerage = self.request.tenant
        messages.success(self.request, f'Ramo "{form.instance.name}" criado com sucesso.')
        return super().form_valid(form)


class LineOfBusinessUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = ('owner', 'manager', 'broker')
    model = LineOfBusiness
    form_class = LineOfBusinessForm
    template_name = 'insurers/lob_form.html'
    success_url = reverse_lazy('insurers:lob_list')

    def get_queryset(self):
        return LineOfBusiness.objects.filter(brokerage=self.request.tenant)

    def form_valid(self, form):
        messages.success(self.request, f'Ramo "{form.instance.name}" atualizado.')
        return super().form_valid(form)