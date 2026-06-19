from base.managers import current_tenant


class TenantMiddleware:
    """Resolve ``request.tenant`` a partir do usuário autenticado.

    Para cada request com usuário autenticado e com ``brokerage``, define:
    - ``request.tenant`` — a ``Brokerage`` do usuário
    - ``current_tenant`` — contextvar disponível em services/tasks (fora da request)

    Usuários sem corretora vinculada (ex.: recém-cadastrados no fluxo de onboarding)
    recebem ``request.tenant = None``. O middleware **não redireciona** nem bloqueia
    — essa lógica pertence a ``TenantQuerysetMixin`` e ``RoleRequiredMixin``.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant = None
        _token = None

        if hasattr(request, 'user') and request.user.is_authenticated:
            tenant = getattr(request.user, 'brokerage', None)

        request.tenant = tenant
        _token = current_tenant.set(tenant)

        try:
            response = self.get_response(request)
        finally:
            current_tenant.reset(_token)

        return response