from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.ReportListView.as_view(), name='report_list'),
    path('<str:report_type>/', views.ReportExportView.as_view(), name='report_export'),
]