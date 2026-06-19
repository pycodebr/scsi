from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('original_filename', 'brokerage', 'content_type', 'object_id', 'uploaded_by', 'size', 'created_at')
    list_filter = ('brokerage', 'content_type')
    search_fields = ('original_filename',)
    readonly_fields = ('created_at', 'updated_at', 'mime_type', 'size')