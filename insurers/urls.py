from django.urls import path

from .views import (
    InsurerCreateView,
    InsurerListView,
    InsurerUpdateView,
    LineOfBusinessCreateView,
    LineOfBusinessListView,
    LineOfBusinessUpdateView,
)

app_name = 'insurers'

urlpatterns = [
    path('seguradoras/', InsurerListView.as_view(), name='insurer_list'),
    path('seguradoras/create/', InsurerCreateView.as_view(), name='insurer_create'),
    path('seguradoras/<int:pk>/edit/', InsurerUpdateView.as_view(), name='insurer_update'),
    path('ramos/', LineOfBusinessListView.as_view(), name='lob_list'),
    path('ramos/create/', LineOfBusinessCreateView.as_view(), name='lob_create'),
    path('ramos/<int:pk>/edit/', LineOfBusinessUpdateView.as_view(), name='lob_update'),
]