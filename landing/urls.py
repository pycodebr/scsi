from django.urls import path
from landing import views

app_name = 'landing'

urlpatterns = [
    path('', views.LandingPageView.as_view(), name='index'),
]
