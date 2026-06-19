from django.db import models
from django.conf import settings
from base.models import TenantAwareModel


class AiSummaryStatus(models.TextChoices):
    IDLE = 'idle', 'Idle'
    PROCESSING = 'processing', 'Processando'
    DONE = 'done', 'Concluído'
    ERROR = 'error', 'Erro'


class Pipeline(TenantAwareModel):
    name = models.CharField('nome', max_length=100)
    is_default = models.BooleanField('pipeline padrão', default=False)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'pipeline'
        verbose_name_plural = 'pipelines'

    def __str__(self):
        return self.name


class Stage(TenantAwareModel):
    pipeline = models.ForeignKey(
        Pipeline,
        on_delete=models.CASCADE,
        related_name='stages',
        verbose_name='pipeline',
    )
    name = models.CharField('nome', max_length=100)
    color = models.CharField('cor (hex)', max_length=7, default='#6c757d')
    order = models.PositiveIntegerField('ordem', default=0)
    is_won = models.BooleanField('ganho', default=False)
    is_lost = models.BooleanField('perdido', default=False)

    class Meta:
        ordering = ('order',)
        verbose_name = 'etapa'
        verbose_name_plural = 'etapas'

    def __str__(self):
        return f'{self.pipeline.name} → {self.name}'


class Deal(TenantAwareModel):
    class Status(models.TextChoices):
        OPEN = 'open', 'Aberto'
        WON = 'won', 'Ganho'
        LOST = 'lost', 'Perdido'

    pipeline = models.ForeignKey(
        Pipeline,
        on_delete=models.CASCADE,
        related_name='deals',
        verbose_name='pipeline',
    )
    stage = models.ForeignKey(
        Stage,
        on_delete=models.PROTECT,
        related_name='deals',
        verbose_name='etapa',
    )
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deals',
        verbose_name='cliente',
    )
    producer = models.ForeignKey(
        'partners.Producer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deals',
        verbose_name='produtor',
    )
    agent = models.ForeignKey(
        'partners.Agent',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deals',
        verbose_name='agente',
    )
    line_of_business = models.ForeignKey(
        'insurers.LineOfBusiness',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deals',
        verbose_name='ramo',
    )
    insurer = models.ForeignKey(
        'insurers.Insurer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deals',
        verbose_name='seguradora',
    )
    proposal = models.ForeignKey(
        'insurance.Proposal',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deals',
        verbose_name='proposta',
    )
    title = models.CharField('título', max_length=200)
    description = models.TextField('descrição', blank=True)
    estimated_value = models.DecimalField(
        'valor estimado',
        max_digits=14,
        decimal_places=2,
        default=0,
    )
    status = models.CharField(
        'status',
        max_length=10,
        choices=Status.choices,
        default=Status.OPEN,
    )
    expected_close_date = models.DateField(
        'previsão de fechamento',
        null=True,
        blank=True,
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
        verbose_name = 'negociação'
        verbose_name_plural = 'negociações'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('crm:deal_detail', kwargs={'pk': self.pk})


class DealStageHistory(TenantAwareModel):
    deal = models.ForeignKey(
        Deal,
        on_delete=models.CASCADE,
        related_name='stage_histories',
        verbose_name='negociação',
    )
    from_stage = models.ForeignKey(
        Stage,
        on_delete=models.SET_NULL,
        null=True,
        related_name='histories_from',
        verbose_name='etapa origem',
    )
    to_stage = models.ForeignKey(
        Stage,
        on_delete=models.CASCADE,
        related_name='histories_to',
        verbose_name='etapa destino',
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='alterado por',
    )
    note = models.TextField('observação', blank=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'histórico de etapa'
        verbose_name_plural = 'históricos de etapa'

    def __str__(self):
        return f'{self.deal.title}: {self.from_stage} → {self.to_stage}'