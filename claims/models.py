from django.db import models
from django.core.exceptions import ValidationError
from base.models import TenantAwareModel


class AiSummaryStatus(models.TextChoices):
    IDLE = 'idle', 'Idle'
    PROCESSING = 'processing', 'Processando'
    DONE = 'done', 'Concluído'
    ERROR = 'error', 'Erro'


class Claim(TenantAwareModel):
    class Status(models.TextChoices):
        OPENED = 'opened', 'Aberto'
        UNDER_ANALYSIS = 'under_analysis', 'Em Análise'
        APPROVED = 'approved', 'Aprovado'
        DENIED = 'denied', 'Negado'
        PAID = 'paid', 'Pago'
        CLOSED = 'closed', 'Fechado'

    policy = models.ForeignKey(
        'insurance.Policy',
        on_delete=models.CASCADE,
        related_name='claims',
        verbose_name='apólice',
    )
    covered_item = models.ForeignKey(
        'insurance.CoveredItem',
        on_delete=models.CASCADE,
        related_name='claims',
        verbose_name='item coberto',
    )
    claim_number = models.CharField('número do sinistro', max_length=50)
    occurrence_date = models.DateField('data da ocorrência')
    notice_date = models.DateField('data do aviso')
    status = models.CharField(
        'status',
        max_length=20,
        choices=Status.choices,
        default=Status.OPENED,
    )
    description = models.TextField('descrição', blank=True)
    claimed_amount = models.DecimalField(
        'valor reclamado',
        max_digits=14,
        decimal_places=2,
        default=0,
    )
    approved_amount = models.DecimalField(
        'valor aprovado',
        max_digits=14,
        decimal_places=2,
        default=0,
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
        verbose_name = 'sinistro'
        verbose_name_plural = 'sinistros'
        constraints = [
            models.UniqueConstraint(
                fields=['brokerage', 'claim_number'],
                name='claim_unique_number_per_brokerage',
            ),
        ]

    def clean(self):
        super().clean()
        if self.occurrence_date and self.notice_date:
            if self.occurrence_date > self.notice_date:
                raise ValidationError({
                    'occurrence_date': 'Data da ocorrência não pode ser posterior ao aviso.',
                })
        if self.covered_item_id and self.policy_id:
            if self.covered_item.policy_id != self.policy_id:
                raise ValidationError({
                    'covered_item': 'Item coberto não pertence à apólice selecionada.',
                })

    def __str__(self):
        return f'{self.claim_number} — {self.get_status_display()}'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('claims:claim_detail', kwargs={'pk': self.pk})