from django.contrib import admin

from branches.models import InsuranceBranch


@admin.register(InsuranceBranch)
class InsuranceBranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active', 'brokerage', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at', 'updated_at']
