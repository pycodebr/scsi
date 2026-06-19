import random
from datetime import date, timedelta
from django.utils import timezone

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from faker import Faker

from clients.models import Client
from claims.models import Claim
from commissions.models import Commission, CommissionSplit
from crm.models import Deal, DealStageHistory, Pipeline, Stage
from documents.models import Document
from insurance.models import (
    CoveredItem,
    Endorsement,
    Policy,
    Proposal,
    Renewal,
)
from insurers.models import Insurer, LineOfBusiness
from notifications.models import Notification
from partners.models import Agent, Producer
from tenants.models import Brokerage, Plan, Subscription
from ai_agents.models import ChatSession, ChatMessage
from accounts.models import User


ItemTypes = CoveredItem.ItemType
ClaimStatus = Claim.Status
DealStatus = Deal.Status
ProposalStatus = Proposal.Status
PolicyStatus = Policy.Status
EndorsementType = Endorsement.Type
EndorsementStatus = Endorsement.Status
RenewalStatus = Renewal.Status
CommissionStatus = Commission.Status
CommissionSplitStatus = CommissionSplit.SplitStatus


BRAZILIAN_STATES = [
    'SP', 'RJ', 'MG', 'RS', 'PR', 'SC', 'BA', 'PE', 'CE', 'GO',
    'PA', 'AM', 'MT', 'DF', 'ES', 'MA', 'PB', 'RN', 'AL', 'PI',
]

LOB_CATEGORIES = {
    'auto': 'Auto',
    'property': 'Propriedade',
    'fleet': 'Frota',
    'travel': 'Viagem',
    'life': 'Vida',
    'equipment': 'Equipamento',
    'other': 'Outro',
}

FAKE_SUMMARY = (
    "Resumo gerado automaticamente para demonstração. "
    "Este texto simula a saída do agente de IA com informações relevantes "
    "sobre a entidade, incluindo pontos-chave, riscos identificados e "
    "recomendações de acompanhamento."
)


class Command(BaseCommand):
    help = 'Popula o banco com dados fictícios para demonstração.'

    def add_arguments(self, parser):
        parser.add_argument('--brokerages', type=int, default=2, help='Número de corretoras a criar (default: 2)')
        parser.add_argument('--flush', action='store_true', help='Remove dados de demonstração antes de criar')
        parser.add_argument('--seed', type=int, default=42, help='Seed determinística para Faker/random (default: 42)')
        parser.add_argument('--with-files', action='store_true', help='Gera arquivos placeholder para Document')
        parser.add_argument('--force', action='store_true', help='Permite rodar com DEBUG=False (produção)')

    def handle(self, *args, **options):
        if not settings.DEBUG and not options['force']:
            raise CommandError(
                'Comando seed_demo não pode ser executado com DEBUG=False. '
                'Use --force para permitir em produção.'
            )

        faker = Faker('pt_BR')
        faker.seed_instance(options['seed'])
        random.seed(options['seed'])

        self.with_files = options['with_files']
        self.stdout.write(self.style.NOTICE('Iniciando seed_demo...'))

        if options['flush']:
            self._flush_demo_data()
            self.stdout.write(self.style.SUCCESS('Dados de demonstração removidos.'))

        num_brokerages = options['brokerages']
        created_counts = {}

        with transaction.atomic():
            for i in range(num_brokerages):
                counts = self._create_brokerage_data(faker, i + 1)
                for key, val in counts.items():
                    created_counts[key] = created_counts.get(key, 0) + val

        self.stdout.write(self.style.SUCCESS('\nSeed demo concluído!'))
        self.stdout.write(self.style.NOTICE('\nResumo por corretora:'))
        for key, val in sorted(created_counts.items()):
            self.stdout.write(f'  {key}: {val}')

    def _flush_demo_data(self):
        from django.apps import apps
        order = [
            DealStageHistory, Notification, ChatSession, ChatMessage,
            CommissionSplit, Commission, Claim, Renewal, Endorsement,
            CoveredItem, Policy, Proposal, Deal, Document,
            Stage, Pipeline, Producer, Agent, Client,
            LineOfBusiness, Insurer,
            Subscription, Brokerage,
        ]
        for model in order:
            model.objects.filter(_demo=True).delete() if hasattr(model, '_demo') else None
        # Fallback: delete all in reverse dependency order
        DealStageHistory.objects.all().delete()
        Notification.objects.all().delete()
        ChatMessage.objects.all().delete()
        ChatSession.objects.all().delete()
        CommissionSplit.objects.all().delete()
        Commission.objects.all().delete()
        Claim.objects.all().delete()
        Renewal.objects.all().delete()
        Endorsement.objects.all().delete()
        CoveredItem.objects.all().delete()
        Policy.objects.all().delete()
        Proposal.objects.all().delete()
        Deal.objects.all().delete()
        Document.objects.all().delete()
        Stage.objects.all().delete()
        Pipeline.objects.all().delete()
        Producer.objects.all().delete()
        Agent.objects.all().delete()
        Client.objects.all().delete()
        LineOfBusiness.objects.all().delete()
        Insurer.objects.all().delete()
        Subscription.objects.all().delete()
        Brokerage.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

    def _create_brokerage_data(self, faker, index):
        counts = {}
        plan, _ = Plan.objects.get_or_create(
            slug=f'plano-demo-{index}',
            defaults={
                'name': f'Plano Demo {index}',
                'price': 299.00 if index == 1 else 599.00,
                'is_available': True,
                'max_users': 10 if index == 1 else 50,
                'features': {'max_clients': 500, 'max_policies': 2000},
            },
        )
        counts['Plan'] = 1

        roles = ['owner', 'manager', 'broker', 'agent', 'producer', 'operational']
        users = {}
        for role in roles:
            user = User.objects.create_user(
                email=f'{role}{index}@demo.com',
                password='demo1234',
                role=role,
                is_active=True,
            )
            users[role] = user

        brokerage = Brokerage.objects.create(
            legal_name=faker.company(),
            trade_name=f'Seguros Demo {index}',
            cnpj=faker.cnpj(),
            susep_code=faker.numerify(text='#####'),
            email=faker.company_email(),
            phone=faker.phone_number(),
            address_street=faker.street_address(),
            address_city=faker.city(),
            address_state=random.choice(BRAZILIAN_STATES),
            address_zip=faker.postcode(),
            is_active=True,
            owner=users['owner'],
            plan=plan,
        )
        counts['Brokerage'] = 1

        User.objects.filter(pk__in=[u.pk for u in users.values()]).update(brokerage=brokerage)

        Subscription.objects.create(
            brokerage=brokerage,
            plan=plan,
            status='active',
            expires_at=timezone.now() + timedelta(days=365),
        )
        counts['Subscription'] = 1
        counts['User'] = len(roles)

        insurers = self._create_insurers(faker, brokerage, counts)
        lines = self._create_lines(faker, brokerage, counts)
        agents, producers = self._create_partners(faker, brokerage, users, counts)
        clients = self._create_clients(faker, brokerage, counts)
        proposals, covered_items_proposals = self._create_proposals(
            faker, brokerage, clients, insurers, lines, producers, agents, counts
        )
        policies, covered_items_policies = self._create_policies(
            faker, brokerage, clients, insurers, lines, producers, agents, proposals, counts
        )
        self._create_claims(faker, brokerage, policies, counts)
        self._create_endorsements(faker, brokerage, policies, counts)
        self._create_renewals(faker, brokerage, policies, counts)
        self._create_commissions(faker, brokerage, policies, agents, producers, counts)
        self._create_crm(faker, brokerage, clients, producers, agents, insurers, lines, proposals, users, counts)
        self._create_notifications(faker, brokerage, users, counts)
        self._create_chat_sessions(faker, brokerage, users, counts)

        return counts

    def _create_insurers(self, faker, brokerage, counts):
        insurers = []
        names = ['Porto Seguro', 'SulAmérica', 'Bradesco Seguros', 'Itaú Seguros', 'HDI Seguros',
                  'Allianz', 'Liberty Seguros', 'Mapfre Seguros', 'Tokio Marine', 'Zurich Seguros']
        for name in names[:5]:
            insurer, _ = Insurer.objects.get_or_create(
                brokerage=brokerage,
                name=name,
                defaults=dict(
                    cnpj=faker.cnpj(),
                    susep_code=faker.numerify(text='#####'),
                    email=faker.company_email(),
                    phone=faker.phone_number(),
                    is_active=True,
                ),
            )
            insurers.append(insurer)
        counts['Insurer'] = len(insurers)
        return insurers

    def _create_lines(self, faker, brokerage, counts):
        lines = []
        cats = list(LOB_CATEGORIES.items())
        for code, name in cats:
            line, _ = LineOfBusiness.objects.get_or_create(
                brokerage=brokerage,
                name=name,
                defaults=dict(
                    code=code.upper(),
                    category=code,
                    is_active=True,
                ),
            )
            lines.append(line)
        counts['LineOfBusiness'] = len(lines)
        return lines

    def _create_partners(self, faker, brokerage, users, counts):
        agents = []
        for i in range(3):
            agents.append(Agent.objects.create(
                brokerage=brokerage,
                entity_type='person',
                name=faker.name(),
                document=faker.cpf(),
                email=faker.email(),
                phone=faker.phone_number(),
                susep_code=faker.numerify(text='#####-#'),
                default_commission_rate=faker.pydecimal(min_value=5, max_value=20, right_digits=2),
                is_active=True,
                user=users.get('agent') if i == 0 else None,
            ))
        counts['Agent'] = len(agents)

        producers = []
        for i in range(4):
            producers.append(Producer.objects.create(
                brokerage=brokerage,
                entity_type=random.choice(['person', 'company']),
                name=faker.name() if i < 2 else faker.company(),
                document=faker.cpf() if i < 2 else faker.cnpj(),
                email=faker.email(),
                phone=faker.phone_number(),
                default_commission_rate=faker.pydecimal(min_value=3, max_value=15, right_digits=2),
                is_active=True,
                agent=agents[i] if i < len(agents) else None,
                user=users.get('producer') if i == 0 else None,
            ))
        counts['Producer'] = len(producers)
        return agents, producers

    def _create_clients(self, faker, brokerage, counts):
        clients = []
        for i in range(15):
            is_pf = i < 10
            clients.append(Client.objects.create(
                brokerage=brokerage,
                person_type='PF' if is_pf else 'PJ',
                name=faker.name() if is_pf else faker.company(),
                trade_name=faker.company() if not is_pf else '',
                document=faker.cpf() if is_pf else faker.cnpj(),
                email=faker.email(),
                phone=faker.phone_number(),
                birth_date=faker.date_of_birth(minimum_age=18, maximum_age=80) if is_pf else None,
                address_street=faker.street_address(),
                address_city=faker.city(),
                address_state=random.choice(BRAZILIAN_STATES),
                address_zip=faker.postcode(),
                notes=faker.text(max_nb_chars=100) if i % 3 == 0 else '',
                ai_summary=FAKE_SUMMARY if i % 5 == 0 else '',
                ai_summary_status='done' if i % 5 == 0 else 'idle',
                is_active=True,
            ))
        counts['Client'] = len(clients)
        return clients

    def _create_proposals(self, faker, brokerage, clients, insurers, lines, producers, agents, counts):
        proposals = []
        covered_items_map = {}
        statuses = list(ProposalStatus)

        for i in range(10):
            status = random.choice(statuses)
            client = random.choice(clients)
            proposal = Proposal.objects.create(
                brokerage=brokerage,
                number=faker.numerify(text='PROP-#####{:04d}'.format(i + 1)),
                client=client,
                insurer=random.choice(insurers),
                line_of_business=random.choice(lines),
                producer=random.choice(producers) if random.random() > 0.3 else None,
                agent=random.choice(agents) if random.random() > 0.3 else None,
                status=status,
                net_premium=faker.pydecimal(min_value=500, max_value=50000, right_digits=2),
                total_premium=faker.pydecimal(min_value=600, max_value=55000, right_digits=2),
                iof=faker.pydecimal(min_value=10, max_value=500, right_digits=2),
                proposed_start_date=faker.date_between(start_date='-180d', end_date='+60d'),
                proposed_end_date=faker.date_between(start_date='+180d', end_date='+540d'),
                payment_terms=random.choice(['Mensal', 'Trimestral', 'Semestral', 'Anual']),
                notes=faker.text(max_nb_chars=150) if i % 3 == 0 else '',
                ai_summary=FAKE_SUMMARY if i % 4 == 0 else '',
                ai_summary_status='done' if i % 4 == 0 else 'idle',
            )
            proposals.append(proposal)

            items = self._create_covered_items(faker, brokerage, proposal, None, lines)
            covered_items_map[proposal.pk] = items

        if proposals:
            Proposal.objects.filter(pk=proposals[0].pk).update(
                ai_summary=FAKE_SUMMARY, ai_summary_status='done'
            )

        counts['Proposal'] = len(proposals)
        counts['CoveredItem'] = counts.get('CoveredItem', 0)
        return proposals, covered_items_map

    def _create_covered_items(self, faker, brokerage, proposal, policy, lines):
        items = []
        num_items = random.randint(1, 3)
        item_types = list(ItemTypes)

        for j in range(num_items):
            item_type = random.choice(item_types)
            attrs = {}
            coverages_list = []
            if item_type == ItemTypes.AUTO:
                attrs = {'marca': faker.company(), 'modelo': faker.word(), 'ano': random.randint(2018, 2025), 'placa': faker.license_plate()}
                coverages_list = ['Casco', 'RCF-V', 'Danos Corporais', 'Danos Materiais']
            elif item_type == ItemTypes.PROPERTY:
                attrs = {'endereco': faker.street_address(), 'tipo': random.choice(['Residencial', 'Comercial', 'Industrial'])}
                coverages_list = ['Incêndio', 'Explosão', 'Roubo', 'Danos Elétricos']
            elif item_type == ItemTypes.LIFE:
                attrs = {'beneficiário': faker.name(), 'parentesco': random.choice(['Cônjuge', 'Filho', 'Pai/Mãe'])}
                coverages_list = ['Morte Natural', 'Morte Acidental', 'Invalidez Permanente']
            else:
                attrs = {'descrição': faker.sentence(nb_words=5)}
                coverages_list = ['Básica', 'Morte Acidental']

            items.append(CoveredItem.objects.create(
                brokerage=brokerage,
                proposal=proposal,
                policy=policy,
                item_type=item_type,
                description=faker.sentence(nb_words=5),
                identifier=faker.numerify(text='ITEM-#####{:04d}'.format(random.randint(1, 9999))),
                insured_amount=faker.pydecimal(min_value=10000, max_value=500000, right_digits=2),
                attributes=attrs,
                coverages=coverages_list,
            ))
        return items

    def _create_policies(self, faker, brokerage, clients, insurers, lines, producers, agents, proposals, counts):
        policies = []
        statuses = [PolicyStatus.ACTIVE, PolicyStatus.EXPIRED, PolicyStatus.CANCELED, PolicyStatus.RENEWED]
        total_items = 0

        for i in range(8):
            status = random.choice(statuses)
            client = random.choice(clients)
            policy = Policy.objects.create(
                brokerage=brokerage,
                policy_number=faker.numerify(text='APOL-#####{:04d}'.format(i + 1)),
                client=client,
                insurer=random.choice(insurers),
                line_of_business=random.choice(lines),
                producer=random.choice(producers) if random.random() > 0.3 else None,
                agent=random.choice(agents) if random.random() > 0.3 else None,
                proposal=random.choice(proposals) if random.random() > 0.5 else None,
                status=status,
                net_premium=faker.pydecimal(min_value=500, max_value=50000, right_digits=2),
                total_premium=faker.pydecimal(min_value=600, max_value=55000, right_digits=2),
                iof=faker.pydecimal(min_value=10, max_value=500, right_digits=2),
                commission_rate=faker.pydecimal(min_value=5, max_value=25, right_digits=2),
                start_date=faker.date_between(start_date='-365d', end_date='+30d'),
                end_date=faker.date_between(start_date='+30d', end_date='+730d'),
                payment_info=random.choice(['Mensal', 'Trimestral', 'Semestral', 'Anual']),
                ai_summary=FAKE_SUMMARY if i % 3 == 0 else '',
                ai_summary_status='done' if i % 3 == 0 else 'idle',
            )
            policies.append(policy)
            self._create_covered_items(faker, brokerage, None, policy, lines)
            total_items += 1

        counts['Policy'] = len(policies)
        counts['CoveredItem'] = counts.get('CoveredItem', 0) + total_items
        return policies, None

    def _create_claims(self, faker, brokerage, policies, counts):
        claims = []
        statuses = list(ClaimStatus)

        for i in range(5):
            if not policies:
                break
            policy = random.choice(policies)
            items = list(CoveredItem.objects.filter(policy=policy, brokerage=brokerage))
            if not items:
                continue
            claim = Claim.objects.create(
                brokerage=brokerage,
                claim_number=faker.numerify(text='SIN-#####{:04d}'.format(i + 1)),
                policy=policy,
                covered_item=random.choice(items),
                occurrence_date=faker.date_between(start_date='-180d', end_date='today'),
                notice_date=faker.date_between(start_date='-180d', end_date='today'),
                status=random.choice(statuses),
                description=faker.text(max_nb_chars=200),
                claimed_amount=faker.pydecimal(min_value=1000, max_value=100000, right_digits=2),
                approved_amount=faker.pydecimal(min_value=500, max_value=80000, right_digits=2) if random.random() > 0.3 else 0,
                ai_summary=FAKE_SUMMARY if i % 3 == 0 else '',
                ai_summary_status='done' if i % 3 == 0 else 'idle',
            )
            claims.append(claim)
        counts['Claim'] = len(claims)
        return claims

    def _create_endorsements(self, faker, brokerage, policies, counts):
        endorsements = []
        types = list(EndorsementType)
        statuses = list(EndorsementStatus)

        for i in range(4):
            policy = random.choice(policies) if policies else None
            if not policy:
                break
            endorsements.append(Endorsement.objects.create(
                brokerage=brokerage,
                policy=policy,
                endorsement_number=faker.numerify(text='END-#####{:04d}'.format(i + 1)),
                type=random.choice(types),
                description=faker.sentence(nb_words=10),
                premium_change=faker.pydecimal(min_value=-5000, max_value=10000, right_digits=2),
                effective_date=faker.date_between(start_date='-90d', end_date='+90d'),
                status=random.choice(statuses),
            ))
        counts['Endorsement'] = len(endorsements)

    def _create_renewals(self, faker, brokerage, policies, counts):
        renewals = []
        for i in range(4):
            policy = random.choice(policies) if policies else None
            if not policy:
                break
            status = random.choice(list(RenewalStatus))
            renewals.append(Renewal.objects.create(
                brokerage=brokerage,
                policy=policy,
                new_policy=None,
                status=status,
                due_date=faker.date_between(start_date='-60d', end_date='+90d'),
                notes=faker.text(max_nb_chars=100) if random.random() > 0.5 else '',
            ))
        counts['Renewal'] = len(renewals)

    def _create_commissions(self, faker, brokerage, policies, agents, producers, counts):
        commissions = []
        splits_count = 0
        statuses = list(CommissionStatus)

        for i in range(5):
            policy = random.choice(policies) if policies else None
            if not policy:
                break
            commission = Commission.objects.create(
                brokerage=brokerage,
                policy=policy,
                base_premium=policy.net_premium if policy else faker.pydecimal(min_value=500, max_value=20000, right_digits=2),
                insurer_rate=faker.pydecimal(min_value=5, max_value=20, right_digits=2),
                insurer_amount=faker.pydecimal(min_value=100, max_value=5000, right_digits=2),
                status=random.choice(statuses),
                reference_date=faker.date_between(start_date='-180d', end_date='today'),
            )
            commissions.append(commission)

            for j, partner in enumerate(agents[:2]):
                splits_count += 1
                CommissionSplit.objects.create(
                    brokerage=brokerage,
                    commission=commission,
                    agent=partner,
                    beneficiary_type='agent',
                    rate=partner.default_commission_rate,
                    amount=commission.insurer_amount * partner.default_commission_rate / 100,
                    status=random.choice(list(CommissionSplitStatus)),
                    paid_at=faker.date_time_between(start_date='-30d', end_date='now') if random.random() > 0.5 else None,
                )
            for j, partner in enumerate(producers[:2]):
                splits_count += 1
                CommissionSplit.objects.create(
                    brokerage=brokerage,
                    commission=commission,
                    producer=partner,
                    beneficiary_type='producer',
                    rate=partner.default_commission_rate,
                    amount=commission.insurer_amount * partner.default_commission_rate / 100,
                    status=random.choice(list(CommissionSplitStatus)),
                    paid_at=faker.date_time_between(start_date='-30d', end_date='now') if random.random() > 0.5 else None,
                )
        counts['Commission'] = len(commissions)
        counts['CommissionSplit'] = splits_count

    def _create_crm(self, faker, brokerage, clients, producers, agents, insurers, lines, proposals, users, counts):
        pipeline = Pipeline.objects.create(
            brokerage=brokerage,
            name='Funil Padrão',
            is_default=True,
        )
        stages_data = [
            ('Contato', '#6c757d', 1, False, False),
            ('Qualificação', '#0d6efd', 2, False, False),
            ('Proposta', '#ffc107', 3, False, False),
            ('Negociação', '#fd7e14', 4, False, False),
            ('Fechado Ganho', '#198754', 5, True, False),
            ('Fechado Perdido', '#dc3545', 6, False, True),
        ]
        stages = []
        for name, color, order, is_won, is_lost in stages_data:
            stages.append(Stage.objects.create(
                brokerage=brokerage,
                pipeline=pipeline,
                name=name,
                color=color,
                order=order,
                is_won=is_won,
                is_lost=is_lost,
            ))
        counts['Pipeline'] = 1
        counts['Stage'] = len(stages)

        deals = []
        deal_statuses = list(DealStatus)
        for i in range(10):
            stage = random.choice(stages)
            deal = Deal.objects.create(
                brokerage=brokerage,
                pipeline=pipeline,
                stage=stage,
                client=random.choice(clients),
                producer=random.choice(producers) if random.random() > 0.3 else None,
                agent=random.choice(agents) if random.random() > 0.3 else None,
                insurer=random.choice(insurers) if random.random() > 0.5 else None,
                line_of_business=random.choice(lines) if random.random() > 0.5 else None,
                proposal=random.choice(proposals) if random.random() > 0.7 else None,
                title=faker.sentence(nb_words=4),
                description=faker.text(max_nb_chars=200),
                estimated_value=faker.pydecimal(min_value=1000, max_value=200000, right_digits=2),
                status=DealStatus.WON if stage.is_won else (DealStatus.LOST if stage.is_lost else DealStatus.OPEN),
                expected_close_date=faker.date_between(start_date='-30d', end_date='+90d'),
                ai_summary=FAKE_SUMMARY if i % 4 == 0 else '',
                ai_summary_status='done' if i % 4 == 0 else 'idle',
            )
            deals.append(deal)

            DealStageHistory.objects.create(
                brokerage=brokerage,
                deal=deal,
                from_stage=None,
                to_stage=stage,
                changed_by=users.get('broker'),
                note=f'Negociação iniciada',
            )

        counts['Deal'] = len(deals)
        counts['DealStageHistory'] = len(deals)

    def _create_notifications(self, faker, brokerage, users, counts):
        notifications = []
        types = ['ai_summary', 'report', 'renewal', 'system']
        all_users = list(users.values())

        for i in range(20):
            notifications.append(Notification.objects.create(
                brokerage=brokerage,
                user=random.choice(all_users),
                type=random.choice(types),
                title=faker.sentence(nb_words=5),
                message=faker.text(max_nb_chars=100),
                url=faker.url(),
                is_read=random.random() > 0.5,
                read_at=faker.date_time_between(start_date='-7d', end_date='now') if random.random() > 0.5 else None,
            ))
        counts['Notification'] = len(notifications)

    def _create_chat_sessions(self, faker, brokerage, users, counts):
        sessions = []
        messages_count = 0

        broker_user = users.get('broker')
        if not broker_user:
            return

        for i in range(3):
            session = ChatSession.objects.create(
                brokerage=brokerage,
                user=broker_user,
                title=f'Conversa sobre {random.choice(["apólices", "sinistros", "clientes", "renovações"])}',
            )
            sessions.append(session)

            for j in range(random.randint(3, 8)):
                ChatMessage.objects.create(
                    session=session,
                    role='user' if j % 2 == 0 else 'assistant',
                    content=faker.text(max_nb_chars=150) if j % 2 == 0 else faker.paragraph(nb_sentences=2),
                )
                messages_count += 1

        counts['ChatSession'] = len(sessions)
        counts['ChatMessage'] = messages_count