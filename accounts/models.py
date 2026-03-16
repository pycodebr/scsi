from django.contrib.auth.models import AbstractUser
from django.db import models

from accounts.managers import UserManager


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('owner', 'Dono'),
        ('manager', 'Gerente'),
        ('agent', 'Agente'),
        ('producer', 'Produtor'),
    ]

    username = None
    email = models.EmailField('Email', unique=True)
    first_name = models.CharField('Nome', max_length=150)
    last_name = models.CharField('Sobrenome', max_length=150)
    phone = models.CharField('Telefone', max_length=20, blank=True, default='')
    cpf = models.CharField('CPF', max_length=14, blank=True, default='')
    role = models.CharField('Papel', max_length=20, choices=ROLE_CHOICES, default='producer')
    avatar = models.ImageField('Foto', upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def get_active_brokerage(self):
        '''Retorna a corretora ativa do usuário (padrão ou primeira).'''
        user_brokerage = self.user_brokerages.filter(
            is_default=True
        ).select_related('brokerage').first()
        if user_brokerage:
            return user_brokerage.brokerage
        user_brokerage = self.user_brokerages.select_related(
            'brokerage'
        ).first()
        if user_brokerage:
            return user_brokerage.brokerage
        return None

    def get_initials(self):
        '''Retorna as iniciais do nome.'''
        first = self.first_name[0] if self.first_name else ''
        last = self.last_name[0] if self.last_name else ''
        return f'{first}{last}'.upper()


class UserBrokerage(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_brokerages',
        verbose_name='Usuário',
    )
    brokerage = models.ForeignKey(
        'brokerages.Brokerage',
        on_delete=models.CASCADE,
        related_name='user_brokerages',
        verbose_name='Corretora',
    )
    is_default = models.BooleanField('Corretora padrão', default=False)
    joined_at = models.DateTimeField('Data de vínculo', auto_now_add=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Vínculo Usuário-Corretora'
        verbose_name_plural = 'Vínculos Usuários-Corretoras'
        unique_together = ['user', 'brokerage']

    def __str__(self):
        return f'{self.user} — {self.brokerage}'
