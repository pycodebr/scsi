from django.urls import path
from . import views

app_name = 'ai_agents'

urlpatterns = [
    path('generate/<str:entity_type>/<int:pk>/', views.GenerateSummaryView.as_view(), name='generate_summary'),
    path('status/<str:entity_type>/<int:pk>/', views.SummaryStatusView.as_view(), name='summary_status'),
    path('chat/', views.ChatSessionListView.as_view(), name='chat'),
    path('chat/create/', views.ChatSessionCreateView.as_view(), name='chat_session_create'),
    path('chat/<int:pk>/', views.ChatSessionListView.as_view(), name='chat_session'),
    path('chat/<int:pk>/rename/', views.ChatSessionRenameView.as_view(), name='chat_session_rename'),
    path('chat/<int:pk>/delete/', views.ChatSessionDeleteView.as_view(), name='chat_session_delete'),
    path('chat/<int:pk>/export/', views.ChatSessionExportView.as_view(), name='chat_session_export'),
    path('chat/<int:pk>/send/', views.ChatMessageSendView.as_view(), name='chat_message_send'),
]