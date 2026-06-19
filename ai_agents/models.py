from django.db import models
from django.conf import settings
from base.models import TenantAwareModel


class ChatSession(TenantAwareModel):
    title = models.CharField('título', max_length=200, default='Nova conversa')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_sessions',
        verbose_name='usuário',
    )

    class Meta:
        ordering = ('-updated_at',)
        verbose_name = 'sessão de chat'
        verbose_name_plural = 'sessões de chat'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('ai_agents:chat_session', kwargs={'pk': self.pk})


class ChatMessage(models.Model):
    class Role(models.TextChoices):
        USER = 'user', 'Usuário'
        ASSISTANT = 'assistant', 'Assistente'
        SYSTEM = 'system', 'Sistema'

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='sessão',
    )
    role = models.CharField('papel', max_length=10, choices=Role.choices)
    content = models.TextField('conteúdo')
    created_at = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'mensagem de chat'
        verbose_name_plural = 'mensagens de chat'

    def __str__(self):
        return f'{self.role}: {self.content[:80]}'