import os
import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from base.models import TenantAwareModel


def document_upload_path(instance, filename):
    """Caminho de upload segregado por tenant: brokerage_<id>/<app>/<uuid>_<filename>."""
    ext = os.path.splitext(filename)[1]
    uuid_name = f'{uuid.uuid4().hex}{ext}'
    app_label = instance.content_type.app_label if instance.content_type else 'misc'
    return f'brokerage_{instance.brokerage_id}/{app_label}/{uuid_name}'


class Document(TenantAwareModel):
    """Anexo genérico — vinculado a qualquer entidade via ContentType + object_id.

    O upload é sempre segregado por ``brokerage_<id>`` e servido **somente**
    por view protegida (seção 16 do PRD). Nunca exposto em rota pública.
    """

    uploaded_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='uploaded_documents',
        verbose_name='enviado por',
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name='tipo do objeto',
    )
    object_id = models.PositiveIntegerField('ID do objeto')
    content_object = GenericForeignKey('content_type', 'object_id')

    file = models.FileField(
        'arquivo',
        upload_to=document_upload_path,
    )
    original_filename = models.CharField('nome original', max_length=255)
    mime_type = models.CharField('tipo MIME', max_length=100, blank=True)
    size = models.PositiveIntegerField('tamanho (bytes)', default=0)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'documento'
        verbose_name_plural = 'documentos'
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return self.original_filename