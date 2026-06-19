from django import forms
from django.core.exceptions import ValidationError

from .models import Document

ALLOWED_MIME_TYPES = (
    'application/pdf',
    'image/jpeg',
    'image/png',
    'image/webp',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/plain',
    'text/markdown',
    'video/mp4',
    'video/quicktime',
    'video/x-msvideo',
    'video/avi',
)

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB


class DocumentUploadForm(forms.Form):
    """Upload de anexo com validação de tipo e tamanho."""

    file = forms.FileField(label='Anexo')
    content_type_id = forms.IntegerField(widget=forms.HiddenInput)
    object_id = forms.IntegerField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        self.tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)

    def clean_file(self):
        f = self.cleaned_data['file']
        if f.size > MAX_UPLOAD_SIZE:
            raise ValidationError(f'O arquivo excede o limite de {MAX_UPLOAD_SIZE // (1024 * 1024)} MB.')
        if hasattr(f, 'content_type') and f.content_type and f.content_type not in ALLOWED_MIME_TYPES:
            raise ValidationError('Tipo de arquivo não permitido.')
        return f