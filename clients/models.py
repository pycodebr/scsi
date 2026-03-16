from django.db import models


class Client(models.Model):
    CLIENT_TYPE_CHOICES = [
        ('individual', 'Pessoa Física'),
        ('company', 'Pessoa Jurídica'),
    ]

    brokerage = models.ForeignKey(
        'brokerages.Brokerage',
        on_delete=models.CASCADE,
        related_name='clients',
        verbose_name='Corretora',
    )
    client_type = models.CharField(
        'Tipo',
        max_length=20,
        choices=CLIENT_TYPE_CHOICES,
        default='individual',
    )
    name = models.CharField('Nome / Razão Social', max_length=255)
    cpf_cnpj = models.CharField('CPF / CNPJ', max_length=18)
    email = models.EmailField('Email', blank=True, default='')
    phone = models.CharField('Telefone', max_length=20, blank=True, default='')
    secondary_phone = models.CharField(
        'Telefone Secundário', max_length=20, blank=True, default=''
    )
    birth_date = models.DateField(
        'Data de Nascimento', null=True, blank=True
    )
    address = models.CharField('Endereço', max_length=500, blank=True, default='')
    city = models.CharField('Cidade', max_length=100, blank=True, default='')
    state = models.CharField('Estado', max_length=2, blank=True, default='')
    zip_code = models.CharField('CEP', max_length=10, blank=True, default='')
    notes = models.TextField('Observações', blank=True, default='')
    is_active = models.BooleanField('Ativo', default=True)
    assigned_producer = models.ForeignKey(
        'agents.Producer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clients',
        verbose_name='Produtor Responsável',
    )
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['name']

    def __str__(self):
        return self.name
