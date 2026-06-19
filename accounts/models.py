from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from base.models import BaseModel


class UserManager(BaseUserManager):
    """Manager do User customizado — cria contas por e-mail (sem username)."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('O e-mail é obrigatório.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser precisa de is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser precisa de is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser, BaseModel):
    """Usuário do sistema, autenticado por e-mail (sem username)."""

    class Role(models.TextChoices):
        OWNER = 'owner', 'Owner'
        MANAGER = 'manager', 'Manager'
        BROKER = 'broker', 'Corretor'
        AGENT = 'agent', 'Agente'
        PRODUCER = 'producer', 'Produtor'
        OPERATIONAL = 'operational', 'Operacional'

    username = None
    email = models.EmailField('e-mail', unique=True)
    brokerage = models.ForeignKey(
        'tenants.Brokerage',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members',
        verbose_name='corretora',
    )
    role = models.CharField(
        'papel',
        max_length=12,
        choices=Role.choices,
        default=Role.OPERATIONAL,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta(AbstractUser.Meta):
        pass

    def __str__(self):
        return self.email
