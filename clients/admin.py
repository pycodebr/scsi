from django.contrib import admin

from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'document', 'person_type', 'email', 'brokerage', 'is_active')
    list_filter = ('person_type', 'is_active', 'brokerage')
    search_fields = ('name', 'document', 'email')
    readonly_fields = ('ai_summary_updated_at',)