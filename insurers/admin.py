from django.contrib import admin

from .models import Insurer, LineOfBusiness


@admin.register(Insurer)
class InsurerAdmin(admin.ModelAdmin):
    list_display = ('name', 'cnpj', 'brokerage', 'is_active')
    list_filter = ('is_active', 'brokerage')
    search_fields = ('name', 'cnpj')


@admin.register(LineOfBusiness)
class LineOfBusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category', 'brokerage', 'is_active')
    list_filter = ('category', 'is_active', 'brokerage')
    search_fields = ('name', 'code')