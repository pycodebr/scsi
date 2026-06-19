from django.http import HttpResponse
from django.views.generic import TemplateView
from django.views import View

from base.mixins import RoleRequiredMixin
from .services import generate_csv, generate_pdf, LABEL_MAP


class ReportListView(RoleRequiredMixin, TemplateView):
    allowed_roles = ('owner', 'manager')
    template_name = 'reports/report_list.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['report_types'] = [{'key': k, 'label': v} for k, v in LABEL_MAP.items()]
        return ctx


class ReportExportView(RoleRequiredMixin, View):
    allowed_roles = ('owner', 'manager')

    def get(self, request, report_type):
        if report_type not in LABEL_MAP:
            return HttpResponse('Relatório inválido', status=400)

        brokerage = request.tenant
        fmt = request.GET.get('format', 'pdf')
        date_from = request.GET.get('date_from') or None
        date_to = request.GET.get('date_to') or None
        status = request.GET.get('status') or None

        if fmt == 'csv':
            csv_data = generate_csv(brokerage, report_type, date_from, date_to, status)
            response = HttpResponse(csv_data, content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="{report_type}.csv"'
            return response

        pdf_data = generate_pdf(brokerage, report_type, date_from, date_to, status)
        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{report_type}.pdf"'
        return response