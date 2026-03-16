from django.urls import path

from agents import views

app_name = 'producers'

urlpatterns = [
    path('', views.ProducerListView.as_view(), name='producer_list'),
    path('create/', views.ProducerCreateView.as_view(), name='producer_create'),
    path('<int:pk>/', views.ProducerDetailView.as_view(), name='producer_detail'),
    path('<int:pk>/edit/', views.ProducerUpdateView.as_view(), name='producer_update'),
    path('<int:pk>/delete/', views.ProducerDeleteView.as_view(), name='producer_delete'),
]
