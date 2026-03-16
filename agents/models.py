from django.db import models


class Agent(models.Model):
    AGENT_TYPE_CHOICES = [
        ('individual', 'Pessoa Física'),
        ('company', 'Pessoa Jurídica'),
    ]

    brokerage = models.ForeignKey(
        'brokerages.Brokerage',
        on_delete=models.CASCADE,
        related_name='agents',
        verbose_name='Corretora',
    )
    agent_type = models.CharField(
        'Tipo',
        max_length=20,
        choices=AGENT_TYPE_CHOICES,
    )
    name = models.CharField('Nome', max_length=255)
    cpf_cnpj = models.CharField('CPF/CNPJ', max_length=18)
    susep_code = models.CharField('Código SUSEP', max_length=20, blank=True, default='')
    email = models.EmailField('Email', blank=True, default='')
    phone = models.CharField('Telefone', max_length=20, blank=True, default='')
    address = models.CharField('Endereço', max_length=500, blank=True, default='')
    city = models.CharField('Cidade', max_length=100, blank=True, default='')
    state = models.CharField('Estado', max_length=2, blank=True, default='')
    zip_code = models.CharField('CEP', max_length=10, blank=True, default='')
    commission_rate = models.DecimalField(
        'Comissão (%)',
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )
    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='agent',
        verbose_name='Usuário',
    )
    notes = models.TextField('Observações', blank=True, default='')
    is_active = models.BooleanField('Ativo', default=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Agente'
        verbose_name_plural = 'Agentes'
        ordering = ['name']

    def __str__(self):
        return self.name


class Producer(models.Model):
    brokerage = models.ForeignKey(
        'brokerages.Brokerage',
        on_delete=models.CASCADE,
        related_name='producers',
        verbose_name='Corretora',
    )
    agent = models.ForeignKey(
        Agent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='producers',
        verbose_name='Agente',
    )
    name = models.CharField('Nome', max_length=255)
    cpf = models.CharField('CPF', max_length=14)
    susep_code = models.CharField('Código SUSEP', max_length=20, blank=True, default='')
    email = models.EmailField('Email', blank=True, default='')
    phone = models.CharField('Telefone', max_length=20, blank=True, default='')
    commission_rate = models.DecimalField(
        'Comissão (%)',
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )
    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='producer',
        verbose_name='Usuário',
    )
    notes = models.TextField('Observações', blank=True, default='')
    is_active = models.BooleanField('Ativo', default=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Produtor'
        verbose_name_plural = 'Produtores'
        ordering = ['name']

    def __str__(self):
        return self.name
