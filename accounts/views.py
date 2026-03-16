from django.contrib.auth import login, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, UpdateView

from accounts.forms import LoginForm, RegisterForm, ProfileForm
from accounts.models import UserBrokerage
from brokerages.models import Brokerage

User = get_user_model()


class LoginView(DjangoLoginView):
    template_name = 'accounts/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('dashboard:index')


class LogoutView(DjangoLogoutView):
    next_page = '/'


class RegisterView(FormView):
    template_name = 'accounts/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('dashboard:index')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard:index')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Create user
        user = User.objects.create_user(
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password'],
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            role='owner',
        )

        # Create brokerage
        brokerage = Brokerage.objects.create(
            cnpj=form.cleaned_data['cnpj'],
            legal_name=form.cleaned_data['legal_name'],
            trade_name=form.cleaned_data.get('trade_name', ''),
            phone=form.cleaned_data.get('brokerage_phone', ''),
            status='active',
        )

        # Create UserBrokerage
        UserBrokerage.objects.create(
            user=user,
            brokerage=brokerage,
            is_default=True,
        )

        # Login
        login(self.request, user)
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, UpdateView):
    template_name = 'accounts/profile.html'
    form_class = ProfileForm
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        return self.request.user
