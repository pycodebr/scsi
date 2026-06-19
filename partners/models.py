from django.db import models
from base.models import TenantAwareModel


class Agent(TenantAwareModel):
    class EntityType(models.TextChoices):
        PERSON = 'person', 'Pessoa Física'
        COMPANY = 'company', 'Pessoa Jurídica'

    entity_type = models.CharField(
        'tipo', max_length=10, choices=EntityType.choices, default=EntityType.PERSON,
    )
    name = models.CharField('nome', max_length=200)
    document = models.CharField('CPF/CNPJ', max_length=18, db_index=True)
    email = models.EmailField('e-mail', blank=True)
    phone = models.CharField('telefone', max_length=20, blank=True)
    susep_code = models.CharField('código SUSEP', max_length=50, blank=True)
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='agent_profiles',
        verbose_name='usuário',
    )
    default_commission_rate = models.DecimalField(
        'taxa de comissão padrão (%)',
        max_digits=5,
        decimal_places=2,
        default=0,
    )
    is_active = models.BooleanField('ativo', default=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'agente'
        verbose_name_plural = 'agentes'
        constraints = [
            models.UniqueConstraint(
                fields=['brokerage', 'document'],
                name='agent_unique_document_per_brokerage',
            ),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('partners:agent_detail', kwargs={'pk': self.pk})


class Producer(TenantAwareModel):
    class EntityType(models.TextChoices):
        PERSON = 'person', 'Pessoa Física'
        COMPANY = 'company', 'Pessoa Jurídica'

    agent = models.ForeignKey(
        Agent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='producers',
        verbose_name='agente',
    )
    entity_type = models.CharField(
        'tipo', max_length=10, choices=EntityType.choices, default=EntityType.PERSON,
    )
    name = models.CharField('nome', max_length=200)
    document = models.CharField('CPF/CNPJ', max_length=18, db_index=True)
    email = models.EmailField('e-mail', blank=True)
    phone = models.CharField('telefone', max_length=20, blank=True)
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='producer_profiles',
        verbose_name='usuário',
    )
    default_commission_rate = models.DecimalField(
        'taxa de comissão padrão (%)',
        max_digits=5,
        decimal_places=2,
        default=0,
    )
    is_active = models.BooleanField('ativo', default=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'produtor'
        verbose_name_plural = 'produtores'
        constraints = [
            models.UniqueConstraint(
                fields=['brokerage', 'document'],
                name='producer_unique_document_per_brokerage',
            ),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('partners:producer_detail', kwargs={'pk': self.pk})