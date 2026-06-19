from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('unread/', views.UnreadCountView.as_view(), name='unread_count'),
    path('<int:pk>/read/', views.MarkReadView.as_view(), name='mark_read'),
    path('', views.ListNotificationsView.as_view(), name='notification_list'),
]