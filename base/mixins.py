from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied

from base.managers import current_tenant


class TenantQuerysetMixin:
    """Filtra automaticamente o queryset da view pelo tenant do usuário.

    A view que herdar este mixin define ``request.tenant`` (via
    ``TenantMiddleware``) e o ``get_queryset`` aplica
    ``Model.objects.for_tenant(request.tenant)``.

    Se o usuário não tiver ``brokerage``, retorna queryset vazio (nenhum dado
    é visível sem tenant).
    """

    def get_queryset(self):
        qs = super().get_queryset()
        tenant = getattr(self.request, 'tenant', None) or current_tenant.get()
        if tenant is None:
            return qs.none()
        return qs.for_tenant(tenant)


PER_PAGE_CHOICES = (10, 20, 50, 100, 200)


class PerPageMixin:
    """Permite que o usuário escolha itens por página via ?per_page=."""

    per_page_default = 10
    per_page_choices = PER_PAGE_CHOICES

    def get_paginate_by(self, queryset):
        per_page = self.request.GET.get('per_page')
        if per_page and per_page.isdigit() and int(per_page) in self.per_page_choices:
            return int(per_page)
        return self.paginate_by or self.per_page_default

    per_page_query_params = ()

    def get_pagination_params(self):
        params = {}
        for key in self.per_page_query_params:
            val = self.request.GET.get(key)
            if val:
                params[key] = val
        return params

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['per_page_choices'] = self.per_page_choices
        ctx['current_per_page'] = self.paginate_by or self.per_page_default
        if hasattr(self, 'request') and self.request.GET.get('per_page'):
            per_page = self.request.GET.get('per_page')
            if per_page.isdigit() and int(per_page) in self.per_page_choices:
                ctx['current_per_page'] = int(per_page)
        ctx['pagination_params'] = self.get_pagination_params()
        return ctx


class RoleRequiredMixin(AccessMixin):
    """Bloqueia o acesso se o usuário não tiver um dos ``allowed_roles``.

    ``allowed_roles`` pode ser uma lista/tupla de strings ou uma string única.
    Exige também que o usuário tenha ``brokerage`` vinculada.
    """

    allowed_roles = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        tenant = getattr(request, 'tenant', None)
        if tenant is None:
            raise PermissionDenied('Usuário sem corretora vinculada.')

        if self.allowed_roles:
            allowed = (
                self.allowed_roles
                if isinstance(self.allowed_roles, (list, tuple))
                else (self.allowed_roles,)
            )
            if request.user.role not in allowed:
                raise PermissionDenied('Papel não autorizado.')

        return super().dispatch(request, *args, **kwargs)