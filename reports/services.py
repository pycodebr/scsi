import csv
import io
from datetime import date

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def _get_queryset(brokerage, report_type, date_from=None, date_to=None, status=None):
    qs_map = {
        'clients': 'clients.models.Client',
        'policies': 'insurance.models.Policy',
        'proposals': 'insurance.models.Proposal',
        'claims': 'claims.models.Claim',
        'renewals': 'insurance.models.Renewal',
        'commissions': 'commissions.models.Commission',
        'insurers': 'insurers.models.Insurer',
    }
    select_related_map = {
        'policies': ['client', 'insurer'],
        'proposals': ['client', 'insurer'],
        'claims': ['policy'],
        'renewals': ['policy', 'new_policy'],
        'commissions': ['policy', 'policy__client', 'policy__insurer'],
    }
    import importlib
    module_path, model_name = qs_map[report_type].rsplit('.', 1)
    module = importlib.import_module(module_path)
    Model = getattr(module, model_name)
    qs = Model.objects.filter(brokerage=brokerage)
    if date_from:
        qs = qs.filter(created_at__date__gte=date_from)
    if date_to:
        qs = qs.filter(created_at__date__lte=date_to)
    if status and hasattr(Model, 'status'):
        qs = qs.filter(status=status)
    if report_type in select_related_map:
        qs = qs.select_related(*select_related_map[report_type])
    return qs


FIELD_MAP = {
    'clients': ['name', 'person_type', 'document', 'email', 'phone', 'is_active'],
    'policies': ['policy_number', 'status', 'client__name', 'insurer__name', 'premium', 'start_date', 'end_date'],
    'proposals': ['number', 'status', 'client__name', 'insurer__name', 'net_premium', 'created_at'],
    'claims': ['claim_number', 'status', 'policy__policy_number', 'occurrence_date', 'claimed_amount', 'approved_amount'],
    'renewals': ['policy__policy_number', 'status', 'due_date', 'notes'],
    'commissions': ['status', 'amount', 'policy__policy_number', 'created_at'],
    'insurers': ['name', 'cnpj', 'susep_code', 'is_active'],
}

HEADER_MAP = {
    'name': 'Nome', 'person_type': 'Tipo', 'document': 'Documento', 'email': 'E-mail',
    'phone': 'Telefone', 'is_active': 'Ativo', 'policy_number': 'Número Apólice',
    'status': 'Status', 'client__name': 'Cliente', 'insurer__name': 'Seguradora',
    'premium': 'Prêmio', 'start_date': 'Início', 'end_date': 'Fim',
    'number': 'Número', 'net_premium': 'Prêmio Líquido', 'created_at': 'Criado em',
    'claim_number': 'Nº Sinistro', 'policy__policy_number': 'Apólice',
    'occurrence_date': 'Data Ocorrência', 'claimed_amount': 'Valor Reclamado',
    'approved_amount': 'Valor Aprovado', 'due_date': 'Vencimento',
    'amount': 'Valor', 'cnpj': 'CNPJ',
    'susep_code': 'SUSEP', 'notes': 'Observações',
}

LABEL_MAP = {
    'clients': 'Carteira de Clientes',
    'policies': 'Apólices',
    'proposals': 'Propostas',
    'claims': 'Sinistros',
    'renewals': 'Renovações',
    'commissions': 'Comissões',
    'insurers': 'Seguradoras',
}


def generate_csv(brokerage, report_type, date_from=None, date_to=None, status=None):
    qs = _get_queryset(brokerage, report_type, date_from, date_to, status)
    fields = FIELD_MAP.get(report_type, [])
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([HEADER_MAP.get(f, f) for f in fields])
    for obj in qs:
        row = []
        for f in fields:
            if '__' in f:
                parts = f.split('__')
                val = obj
                for p in parts:
                    val = getattr(val, p, None)
                    if val is None:
                        break
            else:
                val = getattr(obj, f, '')
            if hasattr(val, 'isoformat'):
                val = val.isoformat()
            elif isinstance(val, bool):
                val = 'Sim' if val else 'Não'
            row.append(val or '')
        writer.writerow(row)
    return output.getvalue()


def generate_pdf(brokerage, report_type, date_from=None, date_to=None, status=None):
    qs = _get_queryset(brokerage, report_type, date_from, date_to, status)
    fields = FIELD_MAP.get(report_type, [])
    label = LABEL_MAP.get(report_type, report_type)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=16, spaceAfter=12)
    subtitle = f"Corretora: {brokerage.trade_name or brokerage.legal_name}"
    if date_from:
        subtitle += f" | De: {date_from}"
    if date_to:
        subtitle += f" | Até: {date_to}"

    elements = [
        Paragraph(f"Relatório — {label}", title_style),
        Paragraph(subtitle, styles['Normal']),
        Spacer(1, 12),
    ]

    data = [[HEADER_MAP.get(f, f) for f in fields]]
    for obj in qs[:500]:
        row = []
        for f in fields:
            if '__' in f:
                parts = f.split('__')
                val = obj
                for p in parts:
                    val = getattr(val, p, None)
                    if val is None:
                        break
            else:
                val = getattr(obj, f, '')
            if hasattr(val, 'isoformat'):
                val = val.isoformat()
            elif isinstance(val, bool):
                val = 'Sim' if val else 'Não'
            row.append(str(val or ''))
        data.append(row)

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4A6CF7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
    ]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()