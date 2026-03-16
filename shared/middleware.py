class TenantMiddleware:
    '''
    Injeta o brokerage ativo no request para uso global.
    '''
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated:
            request.current_brokerage = request.user.get_active_brokerage()
        else:
            request.current_brokerage = None
        return self.get_response(request)
