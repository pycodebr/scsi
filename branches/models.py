from django.db import models


class InsuranceBranch(models.Model):
    brokerage = models.ForeignKey(
        'brokerages.Brokerage',
        on_delete=models.CASCADE,
        related_name='insurance_branches',
        verbose_name='Corretora',
    )
    name = models.CharField('Nome', max_length=255)
    code = models.CharField('Código', max_length=20, blank=True, default='')
    description = models.TextField('Descrição', blank=True, default='')
    is_active = models.BooleanField('Ativo', default=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Ramo de Seguro'
        verbose_name_plural = 'Ramos de Seguro'
        ordering = ['name']
        unique_together = ['brokerage', 'name']

    def __str__(self):
        if self.code:
            return f'{self.name} ({self.code})'
        return self.name
