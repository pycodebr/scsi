from django.contrib import admin

from plans.models import Plan, Subscription, Payment


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_per_user', 'max_users', 'is_free', 'is_active']
    list_filter = ['is_free', 'is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['brokerage', 'plan', 'status', 'started_at', 'expires_at']
    list_filter = ['status', 'plan']
    search_fields = ['brokerage__legal_name']
    inlines = [PaymentInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['subscription', 'amount', 'status', 'payment_date']
    list_filter = ['status']
