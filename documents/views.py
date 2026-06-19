import os

from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import DetailView, FormView

from base.mixins import RoleRequiredMixin, TenantQuerysetMixin
from .forms import DocumentUploadForm
from .models import Document


class ProtectedDocumentDownloadView(View):
    """Serve o arquivo **somente** após verificar autenticação e tenant.

    Fluxo (seção 16.3 do PRD):
    1. Usuário autenticado?
    2. Document pertence ao `request.tenant`?
    3. Retorna FileResponse com Content-Disposition.
    """

    def get(self, request, pk):
        if not request.user.is_authenticated:
            raise Http404

        tenant = getattr(request, 'tenant', None)
        if tenant is None:
            raise Http404

        doc = get_object_or_404(Document, pk=pk, brokerage=tenant)

        if not doc.file:
            raise Http404

        response = FileResponse(
            doc.file.open('rb'),
            as_attachment=True,
            filename=doc.original_filename,
        )
        return response


class DocumentListView(RoleRequiredMixin, TenantQuerysetMixin, DetailView):
    """Lista anexos de um objeto — retorna JSON para ser consumido pelo partial."""

    allowed_roles = ('owner', 'manager', 'broker', 'agent', 'producer', 'operational')
    model = Document
    template_name = 'documents/document_list.html'

    def get_object(self, queryset=None):
        return None

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ct = self.request.GET.get('content_type')
        oid = self.request.GET.get('object_id')
        if ct and oid:
            from django.contrib.contenttypes.models import ContentType
            try:
                ct_obj = ContentType.objects.get(pk=ct)
                ctx['documents'] = Document.objects.filter(
                    content_type=ct_obj,
                    object_id=oid,
                    brokerage=self.request.tenant,
                ).order_by('-created_at')
            except ContentType.DoesNotExist:
                ctx['documents'] = Document.objects.none()
        else:
            ctx['documents'] = Document.objects.none()
        ctx['content_type_id'] = ct
        ctx['object_id'] = oid
        return ctx


class DocumentUploadView(RoleRequiredMixin, FormView):
    """Upload de anexo vinculado a uma entidade via ContentType."""

    allowed_roles = ('owner', 'manager', 'broker')
    form_class = DocumentUploadForm
    template_name = 'documents/document_upload.html'

    def form_valid(self, form):
        from django.contrib.contenttypes.models import ContentType

        ct = ContentType.objects.get_for_id(form.cleaned_data['content_type_id'])
        oid = form.cleaned_data['object_id']

        uploaded_file = form.cleaned_data['file']
        doc = Document.objects.create(
            brokerage=self.request.tenant,
            uploaded_by=self.request.user,
            content_type=ct,
            object_id=oid,
            file=uploaded_file,
            original_filename=uploaded_file.name,
            mime_type=uploaded_file.content_type or '',
            size=uploaded_file.size,
        )

        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'id': doc.pk,
                'original_filename': doc.original_filename,
                'size': doc.size,
                'download_url': f'/documents/{doc.pk}/download/',
                'created_at': doc.created_at.isoformat(),
            })

        from django.contrib import messages
        messages.success(self.request, f'Anexo "{doc.original_filename}" enviado.')
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER', '/')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs