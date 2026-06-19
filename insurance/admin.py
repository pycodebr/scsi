from django.contrib import admin

from .models import CoveredItem, Policy, Proposal


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ('number', 'client', 'insurer', 'status', 'brokerage', 'created_at')
    list_filter = ('status', 'line_of_business', 'brokerage')
    search_fields = ('number', 'client__name')
    raw_id_fields = ('client', 'insurer', 'line_of_business')


@admin.register(CoveredItem)
class CoveredItemAdmin(admin.ModelAdmin):
    list_display = ('description', 'item_type', 'insured_amount', 'proposal', 'policy')
    list_filter = ('item_type',)


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ('policy_number', 'client', 'insurer', 'status', 'brokerage', 'created_at')
    list_filter = ('status', 'line_of_business', 'brokerage')
    search_fields = ('policy_number', 'client__name')
    raw_id_fields = ('client', 'insurer', 'line_of_business', 'proposal')