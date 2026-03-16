from django.contrib import admin

from insurers.models import Insurer


@admin.register(Insurer)
class InsurerAdmin(admin.ModelAdmin):
    list_display = ['name', 'cnpj', 'susep_code', 'email', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'cnpj', 'email']
    readonly_fields = ['created_at', 'updated_at']
