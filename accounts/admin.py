from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin do User customizado (sem username, login por e-mail)."""

    ordering = ('email',)
    list_display = ('email', 'first_name', 'last_name', 'role', 'brokerage', 'is_staff', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff', 'brokerage')
    search_fields = ('email', 'first_name', 'last_name')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações pessoais', {'fields': ('first_name', 'last_name')}),
        ('Corretora e Papel', {'fields': ('brokerage', 'role')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'brokerage'),
        }),
    )
