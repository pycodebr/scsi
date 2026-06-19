from contextvars import ContextVar

from django.db import models

# Tenant ativo no contexto da request (definido pelo TenantMiddleware na Sprint 5).
# Serve como defesa adicional para filtros programáticos por corretora.
current_tenant: ContextVar = ContextVar('current_tenant', default=None)


class TenantQuerySet(models.QuerySet):
    def for_tenant(self, tenant):
        """Restringe o queryset aos registros da corretora informada."""
        return self.filter(brokerage=tenant)


class TenantManager(models.Manager.from_queryset(TenantQuerySet)):
    """Manager tenant-aware das models que herdam de ``TenantAwareModel``.

    O isolamento por corretora é aplicado explicitamente via ``for_tenant`` nas
    views/mixins (ver seções 9.2 e 9.4 do PRD). Nunca exponha um queryset global
    em rotas sensíveis.
    """

    def for_tenant(self, tenant):
        return self.get_queryset().for_tenant(tenant)
