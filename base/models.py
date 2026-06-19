from django.db import models

from base.managers import TenantManager


class BaseModel(models.Model):
    """Base abstrata para toda model de domínio: timestamps automáticos."""

    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        abstract = True
        ordering = ('-created_at',)


class TenantAwareModel(BaseModel):
    """Base abstrata para entidades isoladas por corretora (tenant).

    Toda entidade sensível carrega a FK ``brokerage`` e usa o ``TenantManager``.
    A model concreta ``tenants.Brokerage`` é introduzida na Sprint 5/6.
    """

    brokerage = models.ForeignKey(
        'tenants.Brokerage',
        on_delete=models.CASCADE,
        related_name='%(class)ss',
        db_index=True,
        verbose_name='corretora',
    )

    objects = TenantManager()

    class Meta:
        abstract = True
        indexes = [models.Index(fields=['brokerage'])]
