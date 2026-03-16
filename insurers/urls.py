from django.urls import path

from insurers import views

app_name = 'insurers'

urlpatterns = [
    path('', views.InsurerListView.as_view(), name='insurer_list'),
    path('create/', views.InsurerCreateView.as_view(), name='insurer_create'),
    path('<int:pk>/', views.InsurerDetailView.as_view(), name='insurer_detail'),
    path('<int:pk>/edit/', views.InsurerUpdateView.as_view(), name='insurer_update'),
    path('<int:pk>/delete/', views.InsurerDeleteView.as_view(), name='insurer_delete'),
]
