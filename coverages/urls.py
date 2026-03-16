from django.urls import path

from coverages import views

app_name = 'coverages'

urlpatterns = [
    path('', views.CoverageTypeListView.as_view(), name='coveragetype_list'),
    path('create/', views.CoverageTypeCreateView.as_view(), name='coveragetype_create'),
    path('<int:pk>/', views.CoverageTypeDetailView.as_view(), name='coveragetype_detail'),
    path('<int:pk>/edit/', views.CoverageTypeUpdateView.as_view(), name='coveragetype_update'),
    path('<int:pk>/delete/', views.CoverageTypeDeleteView.as_view(), name='coveragetype_delete'),
]
