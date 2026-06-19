from django.db import models

from base.models import TenantAwareModel


class Insurer(TenantAwareModel):
    """Seguradora parceira da corretora — tenant-aware.

    Cada corretora mantém sua lista de seguradoras. Campo ``is_active``
    permite desativar sem perder histórico de propostas/apólices.
    """

    name = models.CharField('nome', max_length=200)
    cnpj = models.CharField('CNPJ', max_length=18, blank=True)
    susep_code = models.CharField('registro SUSEP', max_length=50, blank=True)
    email = models.EmailField('e-mail', blank=True)
    phone = models.CharField('telefone', max_length=30, blank=True)
    is_active = models.BooleanField('ativo', default=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'seguradora'
        verbose_name_plural = 'seguradoras'
        constraints = [
            models.UniqueConstraint(
                fields=['brokerage', 'name'],
                name='unique_insurer_name_per_brokerage',
            ),
        ]

    def __str__(self):
        return self.name


class LineOfBusiness(TenantAwareModel):
    """Ramo de seguro — tenant-aware.

    Seedado com ramos comuns ao criar a corretora (signal de onboarding).
    O campo ``category`` agrupa ramos afins (Auto, Vida, Patrimonial…).
    ``code`` é o código SUSEP do ramo, opcional na V1.
    """

    class Category(models.TextChoices):
        AUTO = 'auto', 'Automotivo'
        LIFE = 'life', 'Vida'
        PROPERTY = 'property', 'Patrimonial'
        BUSINESS = 'business', 'Empresarial'
        TRAVEL = 'travel', 'Viagem'
        HEALTH = 'health', 'Saúde'
        OTHER = 'other', 'Outro'

    name = models.CharField('nome', max_length=100)
    code = models.CharField('código SUSEP', max_length=20, blank=True)
    category = models.CharField(
        'categoria',
        max_length=12,
        choices=Category.choices,
        default=Category.OTHER,
    )
    is_active = models.BooleanField('ativo', default=True)

    class Meta:
        ordering = ('category', 'name')
        verbose_name = 'ramo'
        verbose_name_plural = 'ramos'
        constraints = [
            models.UniqueConstraint(
                fields=['brokerage', 'name'],
                name='unique_lob_name_per_brokerage',
            ),
        ]

    def __str__(self):
        return self.name