from django.db import models

from base.models import TenantAwareModel


class Client(TenantAwareModel):
    """Cliente PF ou PJ da corretora — isolado por tenant.

    Campos conforme seção 14.5 do PRD:
    ``person_type`` (PF/PJ), ``name``, ``document`` (CPF/CNPJ com unicidade
    por tenant), endereço, contato, e ``ai_summary`` + status para resumo IA.
    """

    class PersonType(models.TextChoices):
        PF = 'PF', 'Pessoa Física'
        PJ = 'PJ', 'Pessoa Jurídica'

    class AiSummaryStatus(models.TextChoices):
        IDLE = 'idle', 'Idle'
        PROCESSING = 'processing', 'Processando'
        DONE = 'done', 'Concluído'
        ERROR = 'error', 'Erro'

    person_type = models.CharField(
        'tipo de pessoa',
        max_length=2,
        choices=PersonType.choices,
        default=PersonType.PF,
    )
    name = models.CharField('nome / razão social', max_length=200)
    trade_name = models.CharField('nome fantasia', max_length=200, blank=True)
    document = models.CharField('CPF / CNPJ', max_length=18, db_index=True)
    email = models.EmailField('e-mail', blank=True)
    phone = models.CharField('telefone', max_length=30, blank=True)
    birth_date = models.DateField('data de nascimento', null=True, blank=True)

    address_street = models.CharField('logradouro', max_length=200, blank=True)
    address_number = models.CharField('número', max_length=20, blank=True)
    address_complement = models.CharField('complemento', max_length=100, blank=True)
    address_neighborhood = models.CharField('bairro', max_length=100, blank=True)
    address_city = models.CharField('cidade', max_length=100, blank=True)
    address_state = models.CharField('UF', max_length=2, blank=True)
    address_zip = models.CharField('CEP', max_length=10, blank=True)

    notes = models.TextField('observações', blank=True)

    ai_summary = models.TextField('resumo IA', blank=True, default='')
    ai_summary_status = models.CharField(
        'status resumo IA',
        max_length=12,
        choices=AiSummaryStatus.choices,
        default=AiSummaryStatus.IDLE,
    )
    ai_summary_updated_at = models.DateTimeField('resumo IA atualizado em', null=True, blank=True)

    is_active = models.BooleanField('ativo', default=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'cliente'
        verbose_name_plural = 'clientes'
        constraints = [
            models.UniqueConstraint(
                fields=['brokerage', 'document'],
                name='unique_client_document_per_brokerage',
            ),
        ]

    def __str__(self):
        return self.name