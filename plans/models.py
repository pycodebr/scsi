from django.db import models


class Plan(models.Model):
    name = models.CharField('Nome', max_length=100)
    slug = models.SlugField('Slug', unique=True)
    description = models.TextField('Descrição', blank=True, default='')
    price_per_user = models.DecimalField('Valor por Usuário/Mês', max_digits=10, decimal_places=2)
    max_users = models.IntegerField('Máx. Usuários', null=True, blank=True, help_text='Vazio = ilimitado')
    features = models.JSONField('Funcionalidades', blank=True, null=True)
    is_free = models.BooleanField('Plano Gratuito', default=False)
    is_active = models.BooleanField('Ativo', default=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Plano'
        verbose_name_plural = 'Planos'
        ordering = ['price_per_user']

    def __str__(self):
        return self.name


class Subscription(models.Model):
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('cancelled', 'Cancelado'),
        ('suspended', 'Suspenso'),
    ]

    brokerage = models.ForeignKey(
        'brokerages.Brokerage',
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Corretora',
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name='subscriptions',
        verbose_name='Plano',
    )
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='active')
    started_at = models.DateTimeField('Início')
    expires_at = models.DateTimeField('Expiração', null=True, blank=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Assinatura'
        verbose_name_plural = 'Assinaturas'
        ordering = ['-started_at']

    def __str__(self):
        return f'{self.brokerage} — {self.plan}'


class Payment(models.Model):
    STATUS_CHOICES = [
        ('paid', 'Pago'),
        ('pending', 'Pendente'),
        ('failed', 'Falhou'),
        ('refunded', 'Reembolsado'),
    ]

    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Assinatura',
    )
    amount = models.DecimalField('Valor', max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField('Data do Pagamento')
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='pending')
    reference = models.CharField('Referência', max_length=100, blank=True, default='')
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'
        ordering = ['-payment_date']

    def __str__(self):
        return f'{self.subscription} — R$ {self.amount}'
