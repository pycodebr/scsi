from django.contrib import admin

from brokerages.models import Brokerage


@admin.register(Brokerage)
class BrokerageAdmin(admin.ModelAdmin):
    list_display = ['legal_name', 'trade_name', 'cnpj', 'status', 'plan', 'created_at']
    list_filter = ['status', 'plan']
    search_fields = ['legal_name', 'trade_name', 'cnpj']
    readonly_fields = ['created_at', 'updated_at']
