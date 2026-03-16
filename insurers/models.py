from django.db import models


class Insurer(models.Model):
    brokerage = models.ForeignKey(
        'brokerages.Brokerage',
        on_delete=models.CASCADE,
        related_name='insurers',
        verbose_name='Corretora',
    )
    name = models.CharField('Nome', max_length=255)
    cnpj = models.CharField('CNPJ', max_length=18, blank=True, default='')
    susep_code = models.CharField('Código SUSEP', max_length=20, blank=True, default='')
    email = models.EmailField('Email', blank=True, default='')
    phone = models.CharField('Telefone', max_length=20, blank=True, default='')
    website = models.URLField('Website', blank=True, default='')
    contact_name = models.CharField('Nome do Contato', max_length=255, blank=True, default='')
    notes = models.TextField('Observações', blank=True, default='')
    is_active = models.BooleanField('Ativo', default=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Seguradora'
        verbose_name_plural = 'Seguradoras'
        ordering = ['name']

    def __str__(self):
        return self.name
