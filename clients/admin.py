from django.contrib import admin

from clients.models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'client_type',
        'cpf_cnpj',
        'email',
        'phone',
        'assigned_producer',
        'is_active',
        'created_at',
    ]
    list_filter = ['client_type', 'is_active', 'state']
    search_fields = ['name', 'cpf_cnpj', 'email']
    readonly_fields = ['created_at', 'updated_at']
