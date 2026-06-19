from django.urls import path

from .views import BrokerageOnboardingView, MyPlanView

app_name = 'tenants'

urlpatterns = [
    path('onboarding/', BrokerageOnboardingView.as_view(), name='onboarding'),
    path('my-plan/', MyPlanView.as_view(), name='my_plan'),
]