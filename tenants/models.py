from django.db import models

from base.models import BaseModel


class Brokerage(BaseModel):
    """Corretora de seguros — o tenant raiz do sistema.

    Herda ``BaseModel`` (timestamps) mas **não** ``TenantAwareModel`` — a própria
    corretora é o tenant; ela não referencia a si mesma.

    O campo ``owner`` aponta para o ``User`` criador (Sprint 6 fará o vínculo
    no fluxo de onboarding). ``plan`` referencia o plano da corretora.
    """

    legal_name = models.CharField('razão social', max_length=200)
    trade_name = models.CharField('nome fantasia', max_length=200, blank=True)
    cnpj = models.CharField('CNPJ', max_length=18, unique=True)
    susep_code = models.CharField('registro SUSEP', max_length=50, blank=True)
    email = models.EmailField('e-mail', blank=True)
    phone = models.CharField('telefone', max_length=30, blank=True)

    # Endereço (opcionais na V1)
    address_street = models.CharField('logradouro', max_length=200, blank=True)
    address_number = models.CharField('número', max_length=20, blank=True)
    address_city = models.CharField('cidade', max_length=100, blank=True)
    address_state = models.CharField('UF', max_length=2, blank=True)
    address_zip = models.CharField('CEP', max_length=10, blank=True)

    owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='owned_brokerages',
        verbose_name='dono',
    )
    plan = models.ForeignKey(
        'tenants.Plan',
        on_delete=models.PROTECT,
        related_name='brokerages',
        verbose_name='plano',
    )
    is_active = models.BooleanField('ativo', default=True)

    class Meta:
        ordering = ('trade_name', 'legal_name')
        verbose_name = 'corretora'
        verbose_name_plural = 'corretoras'

    def __str__(self):
        return self.trade_name or self.legal_name


class Plan(BaseModel):
    """Plano de assinatura — catálogo global, sem tenant.

    Na V1, apenas o plano ``Free`` está disponível; demais exibem "Em breve".
    """

    name = models.CharField('nome', max_length=50)
    slug = models.SlugField('slug', unique=True)
    price = models.DecimalField('preço', max_digits=10, decimal_places=2, default=0)
    is_available = models.BooleanField('disponível', default=False)
    max_users = models.PositiveIntegerField('máx. usuários', null=True, blank=True)
    max_clients = models.PositiveIntegerField('máx. clientes', null=True, blank=True)
    max_policies = models.PositiveIntegerField('máx. apólices', null=True, blank=True)
    features = models.JSONField('funcionalidades', default=list, blank=True)

    class Meta:
        ordering = ('price',)
        verbose_name = 'plano'
        verbose_name_plural = 'planos'

    def __str__(self):
        return self.name


class Subscription(BaseModel):
    """Assinatura da corretora — vínculo entre Brokerage e Plan.

    Na V1, sempre ``active`` no plano Free. OneToOneField na V1 (uma
    corretora = uma assinatura). Em versões futuras pode virar FK para
    permitir múltiplas assinaturas/histórico.
    """

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Ativa'
        PAST_DUE = 'past_due', 'Em atraso'
        CANCELED = 'canceled', 'Cancelada'

    brokerage = models.OneToOneField(
        Brokerage,
        on_delete=models.CASCADE,
        related_name='subscription',
        verbose_name='corretora',
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name='subscriptions',
        verbose_name='plano',
    )
    status = models.CharField(
        'status',
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    started_at = models.DateTimeField('início em', auto_now_add=True)
    expires_at = models.DateTimeField('expira em', null=True, blank=True)

    class Meta:
        verbose_name = 'assinatura'
        verbose_name_plural = 'assinaturas'

    def __str__(self):
        return f'{self.brokerage} — {self.plan} ({self.get_status_display()})'