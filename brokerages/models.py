from django.db import models


class Brokerage(models.Model):
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('inactive', 'Inativo'),
        ('pending_payment', 'Pagamento Pendente'),
        ('overdue', 'Pagamento em Atraso'),
    ]

    cnpj = models.CharField('CNPJ', max_length=18, unique=True)
    legal_name = models.CharField('Razão Social', max_length=255)
    trade_name = models.CharField('Nome Fantasia', max_length=255, blank=True, default='')
    susep_code = models.CharField('Código SUSEP', max_length=20, blank=True, default='')
    email = models.EmailField('Email', blank=True, default='')
    phone = models.CharField('Telefone', max_length=20, blank=True, default='')
    address = models.CharField('Endereço', max_length=500, blank=True, default='')
    city = models.CharField('Cidade', max_length=100, blank=True, default='')
    state = models.CharField('Estado', max_length=2, blank=True, default='')
    zip_code = models.CharField('CEP', max_length=10, blank=True, default='')
    logo = models.ImageField('Logo', upload_to='brokerages/logos/', blank=True, null=True)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='active')
    plan = models.ForeignKey(
        'plans.Plan',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='brokerages',
        verbose_name='Plano',
    )
    default_commission_rate = models.DecimalField(
        'Comissão Padrão (%)',
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Corretora'
        verbose_name_plural = 'Corretoras'
        ordering = ['legal_name']

    def __str__(self):
        return self.trade_name or self.legal_name

    def get_display_name(self):
        return self.trade_name or self.legal_name
