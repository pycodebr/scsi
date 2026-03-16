from django.contrib import admin

from coverages.models import CoverageType


@admin.register(CoverageType)
class CoverageTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'insurance_branch', 'is_active', 'brokerage', 'created_at']
    list_filter = ['is_active', 'insurance_branch']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']
