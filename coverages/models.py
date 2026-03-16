from django.db import models


class CoverageType(models.Model):
    brokerage = models.ForeignKey(
        'brokerages.Brokerage',
        on_delete=models.CASCADE,
        related_name='coverage_types',
        verbose_name='Corretora',
    )
    name = models.CharField('Nome', max_length=255)
    description = models.TextField('Descrição', blank=True, default='')
    insurance_branch = models.ForeignKey(
        'branches.InsuranceBranch',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='coverage_types',
        verbose_name='Ramo de Seguro',
    )
    is_active = models.BooleanField('Ativo', default=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Tipo de Cobertura'
        verbose_name_plural = 'Tipos de Cobertura'
        ordering = ['name']

    def __str__(self):
        return self.name
