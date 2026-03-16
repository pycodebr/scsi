from django.db.models.signals import post_save
from django.dispatch import receiver

from brokerages.models import Brokerage


DEFAULT_BRANCHES = [
    {'name': 'Automóvel', 'code': '0531', 'description': 'Seguro de veículos automotores'},
    {'name': 'Vida Individual', 'code': '0977', 'description': 'Seguro de vida individual'},
    {'name': 'Vida em Grupo', 'code': '0993', 'description': 'Seguro de vida coletivo/grupo'},
    {'name': 'Residencial', 'code': '0114', 'description': 'Seguro residencial'},
    {'name': 'Empresarial', 'code': '0141', 'description': 'Seguro empresarial/patrimonial'},
    {'name': 'Transporte', 'code': '0621', 'description': 'Seguro de transporte de cargas'},
    {'name': 'Viagem', 'code': '1369', 'description': 'Seguro viagem nacional/internacional'},
    {'name': 'Saúde', 'code': '1066', 'description': 'Seguro saúde'},
    {'name': 'Responsabilidade Civil', 'code': '0351', 'description': 'RC geral/profissional'},
    {'name': 'Garantia', 'code': '0775', 'description': 'Seguro garantia'},
    {'name': 'Riscos de Engenharia', 'code': '0167', 'description': 'Seguro para obras e instalações'},
    {'name': 'Condomínio', 'code': '0114', 'description': 'Seguro condomínio'},
    {'name': 'Frota', 'code': '0531', 'description': 'Seguro de frota de veículos'},
    {'name': 'Agrícola', 'code': '0116', 'description': 'Seguro agrícola'},
    {'name': 'Previdência', 'code': '0994', 'description': 'Planos de previdência privada'},
]


@receiver(post_save, sender=Brokerage)
def create_default_branches(sender, instance, created, **kwargs):
    if created:
        from branches.models import InsuranceBranch
        branches = [
            InsuranceBranch(brokerage=instance, **data)
            for data in DEFAULT_BRANCHES
        ]
        InsuranceBranch.objects.bulk_create(branches)
