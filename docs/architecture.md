# Arquitetura

## Visão geral

O SCSI é um SaaS multi tenant onde cada **Brokerage** (corretora) opera de forma isolada. Todos os dados sensíveis filtram por `request.tenant` (FK `brokerage`).

```mermaid
graph TB
    subgraph Internet
        Browser[Navegador]
    end

    subgraph Docker Swarm
        Traefik[Traefik<br/>Reverse Proxy + SSL]
        App[Django App<br/>Gunicorn]
        Worker[Celery Worker]
        Beat[Celery Beat]
    end

    subgraph Storage
        DB[(PostgreSQL 16)]
        RabbitMQ[RabbitMQ]
        Redis[(Redis)]
        Media[/media<br/>arquivos protegidos]
    end

    Browser --> Traefik
    Traefik --> App
    App --> DB
    App --> RabbitMQ
    App --> Redis
    App --> Media
    Worker --> DB
    Worker --> RabbitMQ
    Worker --> Redis
    Worker -->|OpenAI API| LLM[OpenAI GPT]
    Beat --> RabbitMQ
    Beat --> DB
```

## Camadas da aplicação

| Camada | Responsabilidade | Tecnologia |
|---|---|---|
| Reverse Proxy | SSL/TLS, roteamento, rate limiting | Traefik |
| WSGI | Processamento de requests HTTP | Gunicorn + Django |
| Background Jobs | Tasks assíncronas e agendadas | Celery + RabbitMQ |
 cache/locks | Cache de sessão, locks, result backend | Redis |
| Banco de dados | Armazenamento relacional | PostgreSQL 16 |
| IA | Resumos e chat com tools | LangChain + LangGraph + OpenAI |
| Arquivos | Documentos e mídia (servidos com auth) | `/protected-media/` |

## Apps Django

| App | Responsabilidade |
|---|---|
| `base` | Models abstratos (`BaseModel`, `TenantAwareModel`), mixins, managers |
| `tenants` | `Brokerage`, `Plan`, `Subscription`, middleware de tenant |
| `accounts` | `User` customizado (email como USERNAME_FIELD), roles |
| `documents` | `Document` com GenericForeignKey (anexos em qualquer entidade) |
| `clients` | `Client` (PF/PJ), CRUD isolado por tenant |
| `insurers` | `Insurer`, `LineOfBusiness` (catálogos por corretora) |
| `insurance` | `Proposal`, `Policy`, `CoveredItem`, `Endorsement`, `Renewal` |
| `claims` | `Claim` (sinistros) |
| `partners` | `Agent`, `Producer` (hierarquia de parceiros) |
| `commissions` | `Commission`, `CommissionSplit` (financeiro) |
| `crm` | `Pipeline`, `Stage`, `Deal`, `DealStageHistory` (funil de vendas) |
| `notifications` | `Notification` + endpoint de unread + sininho no topbar |
| `ai_agents` | Summary Agent + Chat Agent (LangGraph), tools isoladas por tenant |
| `dashboard` | KPIs, gráficos, funil CRM (sem models próprios) |
| `reports` | Exportação PDF (ReportLab) e CSV (sem models próprios) |

## Padrões arquiteturais

- **Multi tenancy:** FK `brokerage` em toda entidade + `TenantMiddleware` + `TenantQuerysetMixin`
- **Background jobs:** Tarefas pesadas (resumos de IA, e-mails) via Celery
- **IA com isolamento:** Tools recebem `brokerage` por parâmetro — nunca do modelo
- **Arquivos protegidos:** `MEDIA_URL=/protected-media/` com view autenticada
- **Soft delete:** `is_active` em entidades críticas (corretora, cliente, seguradora, etc.)