from django.db import models
from django.conf import settings
from base.models import TenantAwareModel


class Notification(TenantAwareModel):
    class Type(models.TextChoices):
        AI_SUMMARY = 'ai_summary', 'Resumo IA'
        REPORT = 'report', 'Relatório'
        RENEWAL = 'renewal', 'Renovação'
        SYSTEM = 'system', 'Sistema'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='usuário',
    )
    type = models.CharField(
        'tipo',
        max_length=20,
        choices=Type.choices,
        default=Type.SYSTEM,
    )
    title = models.CharField('título', max_length=200)
    message = models.TextField('mensagem', blank=True)
    url = models.URLField('link', blank=True)
    is_read = models.BooleanField('lida', default=False)
    read_at = models.DateTimeField('lida em', null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'notificação'
        verbose_name_plural = 'notificações'

    def __str__(self):
        return f'{self.type}: {self.title}'