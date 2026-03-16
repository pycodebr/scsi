from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from accounts.models import User, UserBrokerage


class UserBrokerageInline(admin.TabularInline):
    model = UserBrokerage
    extra = 1


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['email']
    inlines = [UserBrokerageInline]

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name', 'phone', 'cpf', 'avatar')}),
        ('Permissões', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(UserBrokerage)
class UserBrokerageAdmin(admin.ModelAdmin):
    list_display = ['user', 'brokerage', 'is_default', 'joined_at']
    list_filter = ['is_default']
