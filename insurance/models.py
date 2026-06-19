from django.db import models
from django.core.validators import MinValueValidator

from base.models import TenantAwareModel


class Proposal(TenantAwareModel):
    """Proposta de seguro — tenant-aware.

    Pode originar uma Policy (Sprint 12). Contém itens cobertos (CoveredItem)
    e anexos (Document via GenericFK).
    """

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Rascunho'
        SENT = 'sent', 'Enviada'
        UNDER_ANALYSIS = 'under_analysis', 'Em análise'
        APPROVED = 'approved', 'Aprovada'
        REJECTED = 'rejected', 'Rejeitada'
        CONVERTED = 'converted', 'Convertida'

    class AiSummaryStatus(models.TextChoices):
        IDLE = 'idle', 'Idle'
        PROCESSING = 'processing', 'Processando'
        DONE = 'done', 'Concluído'
        ERROR = 'error', 'Erro'

    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.PROTECT,
        related_name='proposals',
        verbose_name='cliente',
    )
    insurer = models.ForeignKey(
        'insurers.Insurer',
        on_delete=models.PROTECT,
        related_name='proposals',
        verbose_name='seguradora',
    )
    line_of_business = models.ForeignKey(
        'insurers.LineOfBusiness',
        on_delete=models.PROTECT,
        related_name='proposals',
        verbose_name='ramo',
    )
    producer = models.ForeignKey(
        'partners.Producer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='proposals',
        verbose_name='produtor',
    )
    agent = models.ForeignKey(
        'partners.Agent',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='proposals',
        verbose_name='agente',
    )
    number = models.CharField('número', max_length=50)
    status = models.CharField(
        'status',
        max_length=15,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    net_premium = models.DecimalField(
        'prêmio líquido',
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    total_premium = models.DecimalField(
        'prêmio total',
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    iof = models.DecimalField(
        'IOF',
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    proposed_start_date = models.DateField('início vigência proposto', null=True, blank=True)
    proposed_end_date = models.DateField('fim vigência proposto', null=True, blank=True)
    payment_terms = models.CharField('condições de pagamento', max_length=200, blank=True)
    notes = models.TextField('observações', blank=True)

    ai_summary = models.TextField('resumo IA', blank=True, default='')
    ai_summary_status = models.CharField(
        'status resumo IA',
        max_length=12,
        choices=AiSummaryStatus.choices,
        default=AiSummaryStatus.IDLE,
    )
    ai_summary_updated_at = models.DateTimeField('resumo IA atualizado em', null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'proposta'
        verbose_name_plural = 'propostas'
        constraints = [
            models.UniqueConstraint(
                fields=['brokerage', 'number'],
                name='unique_proposal_number_per_brokerage',
            ),
        ]

    def __str__(self):
        return f'{self.number} — {self.client}'


class CoveredItem(TenantAwareModel):
    """Item coberto — vinculado a uma Proposal OU uma Policy (nunca ambos).

    Sprint 13 adiciona CheckConstraint e forms dinâmicos.
    """

    class ItemType(models.TextChoices):
        AUTO = 'auto', 'Automotivo'
        PROPERTY = 'property', 'Patrimonial'
        FLEET = 'fleet', 'Frota'
        TRAVEL = 'travel', 'Viagem'
        LIFE = 'life', 'Vida'
        EQUIPMENT = 'equipment', 'Equipamento'
        OTHER = 'other', 'Outro'

    proposal = models.ForeignKey(
        Proposal,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='proposta',
        null=True,
        blank=True,
    )
    policy = models.ForeignKey(
        'insurance.Policy',
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='apólice',
        null=True,
        blank=True,
    )
    item_type = models.CharField(
        'tipo',
        max_length=12,
        choices=ItemType.choices,
        default=ItemType.OTHER,
    )
    description = models.CharField('descrição', max_length=300)
    identifier = models.CharField('identificador', max_length=100, blank=True, help_text='Placa, chassi, endereço, etc.')
    insured_amount = models.DecimalField(
        'importância segurada',
        max_digits=14,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    attributes = models.JSONField('atributos', default=dict, blank=True, help_text='Dados específicos por tipo (JSON)')
    coverages = models.JSONField('coberturas', default=list, blank=True, help_text='Lista de coberturas e limites (JSON)')

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'item coberto'
        verbose_name_plural = 'itens cobertos'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(proposal__isnull=False, policy__isnull=True)
                | models.Q(proposal__isnull=True, policy__isnull=False),
                name='covered_item_exactly_one_parent',
            ),
        ]

    def __str__(self):
        return f'{self.get_item_type_display()} — {self.description}'


class Policy(TenantAwareModel):
    """Apólice de seguro — tenant-aware.

    Pode ser gerada a partir de uma Proposal via `generate_policy_from_proposal`.
    """

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Ativa'
        CANCELED = 'canceled', 'Cancelada'
        EXPIRED = 'expired', 'Expirada'
        RENEWED = 'renewed', 'Renovada'

    class AiSummaryStatus(models.TextChoices):
        IDLE = 'idle', 'Idle'
        PROCESSING = 'processing', 'Processando'
        DONE = 'done', 'Concluído'
        ERROR = 'error', 'Erro'

    proposal = models.ForeignKey(
        Proposal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='policies',
        verbose_name='proposta de origem',
    )
    policy_number = models.CharField('número da apólice', max_length=50)
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.PROTECT,
        related_name='policies',
        verbose_name='cliente',
    )
    insurer = models.ForeignKey(
        'insurers.Insurer',
        on_delete=models.PROTECT,
        related_name='policies',
        verbose_name='seguradora',
    )
    line_of_business = models.ForeignKey(
        'insurers.LineOfBusiness',
        on_delete=models.PROTECT,
        related_name='policies',
        verbose_name='ramo',
    )
    status = models.CharField(
        'status',
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    net_premium = models.DecimalField(
        'prêmio líquido',
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    total_premium = models.DecimalField(
        'prêmio total',
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    iof = models.DecimalField(
        'IOF',
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    commission_rate = models.DecimalField(
        'taxa de comissão (%)',
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    start_date = models.DateField('início vigência', null=True, blank=True)
    end_date = models.DateField('fim vigência', null=True, blank=True)
    payment_info = models.CharField('informações de pagamento', max_length=300, blank=True)
    producer = models.ForeignKey(
        'partners.Producer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='policies',
        verbose_name='produtor',
    )
    agent = models.ForeignKey(
        'partners.Agent',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='policies',
        verbose_name='agente',
    )

    ai_summary = models.TextField('resumo IA', blank=True, default='')
    ai_summary_status = models.CharField(
        'status resumo IA',
        max_length=12,
        choices=AiSummaryStatus.choices,
        default=AiSummaryStatus.IDLE,
    )
    ai_summary_updated_at = models.DateTimeField('resumo IA atualizado em', null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'apólice'
        verbose_name_plural = 'apólices'
        constraints = [
            models.UniqueConstraint(
                fields=['brokerage', 'policy_number'],
                name='unique_policy_number_per_brokerage',
            ),
        ]

    def __str__(self):
        return self.policy_number

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('insurance:policy_detail', kwargs={'pk': self.pk})


class Endorsement(TenantAwareModel):
    """Endosso — alteração em apólice. Tipos: aumento, redução, cancelamento, alteração cadastral."""

    class Type(models.TextChoices):
        INCREASE = 'increase', 'Aumento'
        DECREASE = 'decrease', 'Redução'
        CANCELLATION = 'cancellation', 'Cancelamento'
        DATA_CHANGE = 'data_change', 'Alteração Cadastral'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendente'
        APPROVED = 'approved', 'Aprovado'
        REJECTED = 'rejected', 'Rejeitado'

    policy = models.ForeignKey(
        Policy,
        on_delete=models.CASCADE,
        related_name='endorsements',
        verbose_name='apólice',
    )
    endorsement_number = models.CharField('número do endosso', max_length=50)
    type = models.CharField('tipo', max_length=20, choices=Type.choices)
    description = models.TextField('descrição', blank=True)
    premium_change = models.DecimalField(
        'variação de prêmio',
        max_digits=14,
        decimal_places=2,
        default=0,
        help_text='Positivo para aumento, negativo para redução.',
    )
    effective_date = models.DateField('data de vigência')
    status = models.CharField(
        'status',
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'endosso'
        verbose_name_plural = 'endossos'
        constraints = [
            models.UniqueConstraint(
                fields=['brokerage', 'policy', 'endorsement_number'],
                name='unique_endorsement_number_per_policy',
            ),
        ]

    def __str__(self):
        return f'{self.endorsement_number} — {self.get_type_display()}'

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and self.type == self.Type.CANCELLATION and self.status == self.Status.APPROVED:
            self.policy.status = Policy.Status.CANCELED
            self.policy.save(update_fields=['status', 'updated_at'])

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('insurance:endorsement_detail', kwargs={'pk': self.pk})


class Renewal(TenantAwareModel):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendente'
        IN_PROGRESS = 'in_progress', 'Em Andamento'
        RENEWED = 'renewed', 'Renovada'
        LOST = 'lost', 'Perdida'
        NOT_RENEWED = 'not_renewed', 'Não Renovada'

    policy = models.ForeignKey(
        Policy,
        on_delete=models.CASCADE,
        related_name='renewals',
        verbose_name='apólice original',
    )
    new_policy = models.ForeignKey(
        Policy,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='renewed_from',
        verbose_name='nova apólice',
    )
    status = models.CharField(
        'status',
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    due_date = models.DateField('data de vencimento')
    notes = models.TextField('observações', blank=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'renovação'
        verbose_name_plural = 'renovações'

    def __str__(self):
        return f'{self.policy.policy_number} — {self.get_status_display()}'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('insurance:renewal_detail', kwargs={'pk': self.pk})