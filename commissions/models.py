from decimal import Decimal
from django.db import models
from base.models import TenantAwareModel


class Commission(TenantAwareModel):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendente'
        RECEIVED = 'received', 'Recebida'
        PAID = 'paid', 'Paga'

    policy = models.ForeignKey(
        'insurance.Policy',
        on_delete=models.CASCADE,
        related_name='commissions',
        verbose_name='apólice',
    )
    base_premium = models.DecimalField(
        'prêmio base',
        max_digits=14,
        decimal_places=2,
        default=Decimal('0'),
    )
    insurer_rate = models.DecimalField(
        'taxa da seguradora (%)',
        max_digits=5,
        decimal_places=2,
        default=Decimal('0'),
        help_text='Percentual pago pela seguradora ao corretor.',
    )
    insurer_amount = models.DecimalField(
        'valor recebido pela corretora',
        max_digits=14,
        decimal_places=2,
        default=Decimal('0'),
    )
    status = models.CharField(
        'status',
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    reference_date = models.DateField(
        'data de referência',
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'comissão'
        verbose_name_plural = 'comissões'

    def __str__(self):
        return f'Comissão {self.pk} — {self.policy.policy_number}'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('commissions:commission_detail', kwargs={'pk': self.pk})


class CommissionSplit(TenantAwareModel):
    class BeneficiaryType(models.TextChoices):
        AGENT = 'agent', 'Agente'
        PRODUCER = 'producer', 'Produtor'

    class SplitStatus(models.TextChoices):
        PENDING = 'pending', 'Pendente'
        PAID = 'paid', 'Pago'

    commission = models.ForeignKey(
        Commission,
        on_delete=models.CASCADE,
        related_name='splits',
        verbose_name='comissão',
    )
    beneficiary_type = models.CharField(
        'tipo de beneficiário',
        max_length=10,
        choices=BeneficiaryType.choices,
    )
    agent = models.ForeignKey(
        'partners.Agent',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='commission_splits',
        verbose_name='agente',
    )
    producer = models.ForeignKey(
        'partners.Producer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='commission_splits',
        verbose_name='produtor',
    )
    rate = models.DecimalField(
        'taxa de repasse (%)',
        max_digits=5,
        decimal_places=2,
        default=Decimal('0'),
    )
    amount = models.DecimalField(
        'valor do repasse',
        max_digits=14,
        decimal_places=2,
        default=Decimal('0'),
    )
    status = models.CharField(
        'status',
        max_length=20,
        choices=SplitStatus.choices,
        default=SplitStatus.PENDING,
    )
    paid_at = models.DateTimeField('pago em', null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'repasse'
        verbose_name_plural = 'repasses'

    def __str__(self):
        beneficiary = self.agent or self.producer
        return f'Repasse {self.pk} — {beneficiary}'