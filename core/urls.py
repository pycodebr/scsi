from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('landing.urls')),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('agents/', include('agents.urls')),
    path('producers/', include('agents.producer_urls')),
    path('clients/', include('clients.urls')),
    path('insurers/', include('insurers.urls')),
    path('branches/', include('branches.urls')),
    path('coverages/', include('coverages.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
