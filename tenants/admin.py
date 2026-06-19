from django.contrib import admin

from .models import Brokerage, Plan, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'price', 'is_available', 'max_users', 'max_clients', 'max_policies')
    list_filter = ('is_available',)
    search_fields = ('name', 'slug')
    ordering = ('price',)


@admin.register(Brokerage)
class BrokerageAdmin(admin.ModelAdmin):
    list_display = ('trade_name', 'legal_name', 'cnpj', 'plan', 'is_active')
    list_filter = ('is_active', 'plan')
    search_fields = ('legal_name', 'trade_name', 'cnpj')
    ordering = ('trade_name',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('brokerage', 'plan', 'status', 'started_at')
    list_filter = ('status', 'plan')
    ordering = ('-started_at',)