from django.db import models


class TenantMixin:
    '''
    Mixin para filtrar querysets pelo brokerage do usuário logado.
    Usar em todas as CBVs que listam ou detalham registros.
    '''
    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role == 'admin':
            return qs
        brokerage = self.request.user.get_active_brokerage()
        return qs.filter(brokerage=brokerage)

    def form_valid(self, form):
        if hasattr(form.instance, 'brokerage') and not form.instance.brokerage_id:
            form.instance.brokerage = self.request.user.get_active_brokerage()
        return super().form_valid(form)


class RoleScopedMixin:
    '''
    Mixin para filtrar dados conforme o papel do usuário.
    Combinar com TenantMixin.
    '''
    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if user.role in ('admin', 'owner', 'manager'):
            return qs

        if user.role == 'agent':
            agent = getattr(user, 'agent', None)
            if agent:
                producer_ids = agent.producers.values_list('id', flat=True)
                return qs.filter(
                    models.Q(agent=agent) |
                    models.Q(producer__in=producer_ids)
                )
            return qs.none()

        if user.role == 'producer':
            producer = getattr(user, 'producer', None)
            if producer:
                return qs.filter(producer=producer)
            return qs.none()

        return qs.none()
