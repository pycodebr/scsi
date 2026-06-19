from django.urls import path
from . import views

app_name = 'crm'

urlpatterns = [
    path('pipelines/', views.PipelineListView.as_view(), name='pipeline_list'),
    path('pipelines/create/', views.PipelineCreateView.as_view(), name='pipeline_create'),
    path('pipelines/<int:pk>/edit/', views.PipelineUpdateView.as_view(), name='pipeline_update'),
    path('stages/create/', views.StageCreateView.as_view(), name='stage_create'),
    path('negociacoes/', views.DealListView.as_view(), name='deal_list'),
    path('negociacoes/create/', views.DealCreateView.as_view(), name='deal_create'),
    path('negociacoes/<int:pk>/', views.DealDetailView.as_view(), name='deal_detail'),
    path('negociacoes/<int:pk>/edit/', views.DealUpdateView.as_view(), name='deal_update'),
    path('kanban/', views.DealKanbanView.as_view(), name='deal_kanban'),
    path('kanban/json/', views.DealKanbanJsonView.as_view(), name='deal_kanban_json'),
    path('negociacoes/<int:pk>/move/', views.DealMoveStageView.as_view(), name='deal_move_stage'),
]