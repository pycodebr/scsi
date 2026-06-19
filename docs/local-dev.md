# Desenvolvimento Local

## Pré-requisitos

- Python 3.13+
- Docker + Docker Compose
- Git

## Subir o ambiente

### 1. Clonar e configurar

```bash
git clone <repo-url> scsi && cd scsi
cp .env.example .env
# Editar .env com valores locais (DEBUG=True, DATABASE_URL, etc.)
```

### 2. Subir com Docker Compose

```bash
docker compose up --build
```

Isso sobe:

| Serviço | Porta | Descrição |
|---|---|---|
| `app` | 8000 | Django (runserver) |
| `db` | 5432 | PostgreSQL 16 |
| `rabbitmq` | 5672/15672 | RabbitMQ (broker + management UI) |
| `redis` | 6379 | Redis (cache + result backend) |
| `celery_worker` | — | Celery worker |
| `celery_beat` | — | Celery beat (scheduler) |

O `entrypoint.sh` roda `migrate` e `collectstatic` automaticamente quando `RUN_MIGRATIONS=1`.

### 3. Criar superusuário

```bash
docker compose exec app python manage.py createsuperuser
```

### 4. Popular dados de demonstração (opcional)

```bash
docker compose exec app python manage.py seed_demo
```

Ver detalhes em [Comando seed_demo](#comando-seed_demo).

### 5. Acessar

- App: http://localhost:8000
- Admin: http://localhost:8000/admin
- RabbitMQ Management: http://localhost:15672 (user/pass do .env)

## Desenvolvimento sem Docker

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Configurar .env com banco local ou omitir DATABASE_URL para SQLite
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Para Celery local:

```bash
celery -A core worker -l info
celery -A core beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

## Estrutura de diretórios

```
scsi/
├── base/           # Models abstratos, mixins, managers
├── tenants/        # Brokerage, Plan, Subscription, middleware
├── accounts/       # User customizado, login/logout
├── documents/      # Document com GenericForeignKey
├── clients/        # Client (PF/PJ)
├── insurers/       # Insurer, LineOfBusiness
├── insurance/      # Proposal, Policy, CoveredItem, Endorsement, Renewal
├── claims/         # Claim
├── partners/       # Agent, Producer
├── commissions/    # Commission, CommissionSplit
├── crm/            # Pipeline, Stage, Deal, DealStageHistory
├── notifications/  # Notification + unread API
├── ai_agents/      # Summary Agent, Chat Agent, tools, tasks
├── dashboard/      # DashboardView (sem models)
├── reports/        # ReportListView, ReportExportView (PDF/CSV)
├── core/           # settings.py, urls.py, wsgi.py
├── templates/      # Templates HTML (Duralux/Bootstrap 5)
├── static/         # Arquivos estáticos
├── docs/           # Documentação MKDocs
├── docker-compose.yml
├── Dockerfile
├── entrypoint.sh
├── requirements.txt
├── mkdocs.yml
└── .env.example
```

## Comando seed_demo

O management command `seed_demo` popula o banco com dados fictícios realistas para demonstrações:

```bash
python manage.py seed_demo                    # padrão: 2 corretoras, seed 42
python manage.py seed_demo --brokerages 3     # 3 corretoras
python manage.py seed_demo --flush            # limpa dados demo antes
python manage.py seed_demo --seed 99          # seed determinística
python manage.py seed_demo --with-files       # gera arquivos placeholder
python manage.py seed_demo --force            # permite rodar com DEBUG=False
```

O comando aborta se `DEBUG=False` sem `--force` (segurança contra execução em produção).