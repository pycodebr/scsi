"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from django.views.generic import TemplateView


def health_check(request):
    """Endpoint leve para healthcheck do container/load balancer.

    Não acessa banco nem exige autenticação — apenas confirma que o processo
    web está de pé e respondendo. Usado pelo HEALTHCHECK do Docker Swarm e pelo
    healthcheck do load balancer do Traefik.
    """
    return JsonResponse({'status': 'ok'})


class LandingPageView(TemplateView):
    template_name = 'landing.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            from django.shortcuts import redirect
            return redirect('/dashboard/')
        return super().get(request, *args, **kwargs)

urlpatterns = [
    path('health/', health_check, name='health'),
    path('admin/', admin.site.urls),
    path('', LandingPageView.as_view(), name='landing'),
    path('dashboard/', include('dashboard.urls')),
    path('accounts/', include('accounts.urls')),
    path('tenants/', include('tenants.urls')),
    path('documents/', include('documents.urls')),
    path('clientes/', include('clients.urls')),
    path('seguradoras/', include('insurers.urls')),
    path('insurance/', include('insurance.urls')),
    path('sinistros/', include('claims.urls')),
    path('parceiros/', include('partners.urls')),
    path('comissoes/', include('commissions.urls')),
    path('crm/', include('crm.urls')),
    path('notifications/', include('notifications.urls')),
    path('ai/', include('ai_agents.urls')),
    path('relatorios/', include('reports.urls')),
]
