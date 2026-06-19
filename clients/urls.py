from django.urls import path

from .views import ClientCreateView, ClientDetailView, ClientListView, ClientUpdateView

app_name = 'clients'

urlpatterns = [
    path('', ClientListView.as_view(), name='client_list'),
    path('create/', ClientCreateView.as_view(), name='client_create'),
    path('<int:pk>/', ClientDetailView.as_view(), name='client_detail'),
    path('<int:pk>/edit/', ClientUpdateView.as_view(), name='client_update'),
]