from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from base.mixins import RoleRequiredMixin, TenantQuerysetMixin
from .forms import (
    EmailAuthenticationForm,
    MemberCreateForm,
    MemberUpdateForm,
    UserRegistrationForm,
    UserProfileForm,
)
from .models import User


class RegisterView(CreateView):
    """Cadastro de usuário; autentica e redireciona ao onboarding."""

    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('tenants:onboarding')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object, backend='accounts.backends.EmailBackend')
        messages.success(self.request, 'Conta criada com sucesso. Bem-vindo(a)!')
        return response


class EmailLoginView(LoginView):
    """Login por e-mail usando o template do Design System."""

    template_name = 'accounts/login.html'
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True


class ProfileView(LoginRequiredMixin, UpdateView):
    """Edição do perfil do próprio usuário autenticado."""

    model = User
    form_class = UserProfileForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Perfil atualizado.')
        return super().form_valid(form)


class MemberListView(RoleRequiredMixin, ListView):
    """Lista membros da corretora — owner/manager."""

    allowed_roles = ('owner', 'manager')
    model = User
    template_name = 'accounts/member_list.html'
    context_object_name = 'members'

    def get_queryset(self):
        return (
            User.objects
            .filter(brokerage=self.request.tenant, is_active=True)
            .order_by('role', 'first_name')
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['max_users'] = self.request.tenant.plan.max_users
        ctx['current_count'] = self.get_queryset().count()
        return ctx


class MemberCreateView(RoleRequiredMixin, CreateView):
    """Cria membro dentro do tenant — owner/manager."""

    allowed_roles = ('owner', 'manager')
    model = User
    form_class = MemberCreateForm
    template_name = 'accounts/member_form.html'
    success_url = reverse_lazy('accounts:member_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['brokerage'] = self.request.tenant
        kwargs['max_users'] = self.request.tenant.plan.max_users
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'Membro {form.instance.email} criado com sucesso.')
        return super().form_valid(form)


class MemberUpdateView(RoleRequiredMixin, UpdateView):
    """Atualiza membro dentro do tenant — owner/manager."""

    allowed_roles = ('owner', 'manager')
    model = User
    form_class = MemberUpdateForm
    template_name = 'accounts/member_form.html'
    success_url = reverse_lazy('accounts:member_list')

    def get_queryset(self):
        return User.objects.filter(brokerage=self.request.tenant)

    def form_valid(self, form):
        messages.success(self.request, f'Membro {form.instance.email} atualizado.')
        return super().form_valid(form)
