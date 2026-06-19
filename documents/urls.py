from django.urls import path

from .views import DocumentListView, DocumentUploadView, ProtectedDocumentDownloadView

app_name = 'documents'

urlpatterns = [
    path('<int:pk>/download/', ProtectedDocumentDownloadView.as_view(), name='download'),
    path('list/', DocumentListView.as_view(), name='list'),
    path('upload/', DocumentUploadView.as_view(), name='upload'),
]