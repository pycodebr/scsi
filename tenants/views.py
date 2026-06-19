from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView

from .forms import BrokerageOnboardingForm
from .models import Brokerage, Plan, Subscription
from accounts.models import User


class BrokerageOnboardingView(LoginRequiredMixin, CreateView):
    """Cria a corretora + vincula o usuário + assinatura Free — transação atômica.

    Redireciona para a página do plano após a criação. Se o usuário já tem
    corretora, redireciona direto (sem exibir o formulário).
    """

    model = Brokerage
    form_class = BrokerageOnboardingForm
    template_name = 'tenants/onboarding.html'
    success_url = reverse_lazy('tenants:my_plan')

    def dispatch(self, request, *args, **kwargs):
        if hasattr(request.user, 'brokerage') and request.user.brokerage:
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        free_plan = Plan.objects.get(slug='free')
        with transaction.atomic():
            brokerage = form.save(commit=False)
            brokerage.owner = self.request.user
            brokerage.plan = free_plan
            brokerage.save()

            Subscription.objects.create(
                brokerage=brokerage,
                plan=free_plan,
                status=Subscription.Status.ACTIVE,
            )

            self.request.user.brokerage = brokerage
            self.request.user.role = User.Role.OWNER
            self.request.user.save(update_fields=['brokerage', 'role'])

        messages.success(self.request, f'Corretora "{brokerage}" criada com sucesso no plano Free!')
        return redirect(self.success_url)


class MyPlanView(LoginRequiredMixin, DetailView):
    """Página 'Meu Plano' — mostra o plano atual da corretora."""

    template_name = 'tenants/my_plan.html'
    context_object_name = 'subscription'

    def get_object(self, queryset=None):
        brokerage = self.request.user.brokerage
        if brokerage is None:
            return None
        return getattr(brokerage, 'subscription', None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['plans'] = Plan.objects.order_by('price')
        context['brokerage'] = self.request.user.brokerage
        return context