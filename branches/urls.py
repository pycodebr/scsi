from django.urls import path

from branches import views

app_name = 'branches'

urlpatterns = [
    path('', views.InsuranceBranchListView.as_view(), name='branch_list'),
    path('create/', views.InsuranceBranchCreateView.as_view(), name='branch_create'),
    path('<int:pk>/', views.InsuranceBranchDetailView.as_view(), name='branch_detail'),
    path('<int:pk>/edit/', views.InsuranceBranchUpdateView.as_view(), name='branch_update'),
    path('<int:pk>/delete/', views.InsuranceBranchDeleteView.as_view(), name='branch_delete'),
]
