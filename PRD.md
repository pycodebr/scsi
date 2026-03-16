# PRD — SCSI: Sistema de Corretora de Seguros Inteligente

**Versão:** 1.1
**Data:** 16/03/2026
**Autor:** Felipe — PycodeBR Treinamentos
**Status:** Draft

### Changelog

| Versão | Data | Alterações |
|---|---|---|
| 1.0 | 16/03/2026 | Versão inicial do PRD |
| 1.1 | 16/03/2026 | Ramos de seguro como entidade CRUD; Itens segurados vinculados a propostas/apólices; Sinistro vinculado a item segurado; Hierarquia Dono/Agente/Produtor; Gestão de comissões e repasses |

---

## 1. Visão Geral do Produto

### 1.1 Resumo Executivo

O **SCSI (Sistema de Corretora de Seguros Inteligente)** é uma plataforma SaaS de gestão completa para corretoras de seguros, desenvolvida com **Python**, **Django 6.0** e frameworks de Inteligência Artificial (**LangChain/LangGraph**). O sistema oferece gestão de clientes, apólices, propostas, sinistros, endossos, renovações e negociações em formato CRM, tudo integrado com um agente de IA que gera insights, resumos e recomendações de cross/up selling diretamente na interface.

### 1.2 Problema

Corretoras de seguros de pequeno e médio porte geralmente operam com planilhas, sistemas legados ou ferramentas genéricas que não atendem às necessidades específicas do setor. Falta integração entre CRM, gestão de apólices, controle de sinistros e análise inteligente de dados. Isso resulta em perda de renovações, oportunidades de venda e controle financeiro deficiente. Além disso, o controle de repasse de comissões entre corretora, agentes e produtores é frequentemente manual e propenso a erros.

### 1.3 Solução

Um sistema web unificado, multi-tenant, com:

- Gestão completa do ciclo de vida do seguro (proposta → apólice → renovação/endosso/sinistro)
- Controle detalhado de itens segurados por apólice/proposta
- Hierarquia operacional real: Corretora → Agentes → Produtores
- Gestão de comissões e repasses com cálculos automáticos
- CRM integrado com visão grid e kanban
- Dashboard com métricas e KPIs da corretora
- Agente de IA integrado que analisa dados e gera insights em tempo real
- Modelo SaaS com planos e onboarding simplificado

### 1.4 Público-Alvo

- Corretoras de seguros de pequeno e médio porte
- Corretores autônomos
- Gestores e administradores de corretoras

---

## 2. Stack Tecnológica

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.13+ |
| Framework Web | Django 6.0 |
| Banco de Dados | SQLite (padrão Django) |
| IA / Agente | LangChain, LangGraph, OpenAI API |
| Frontend | Django Templates + Design System customizado |
| Autenticação | Sistema nativo do Django (customizado com email) |
| Variáveis de Ambiente | python-decouple ou django-environ (.env) |

### 2.1 Convenções de Código

- **Idioma do código:** Inglês
- **Idioma da interface:** Português brasileiro
- **Style guide:** PEP 08
- **Aspas:** Sempre aspas simples (`'`) quando possível
- **Views:** Class Based Views (CBVs) preferencialmente
- **Signals:** Arquivo `signals.py` dedicado dentro de cada app correspondente
- **Models:** Todo model deve conter `created_at` e `updated_at`
- **Design:** Respeitar rigorosamente o design system definido em `design_system/design-system.html`
- **Docker:** Não implementar
- **Testes:** Não implementar

---

## 3. Arquitetura do Sistema

### 3.1 Modelo Multi-Tenant

O SCSI usa o modelo **multi-tenant compartilhado** (shared database, shared schema). Todas as corretoras compartilham o mesmo banco de dados, mas os dados são isolados por:

- Chave estrangeira `brokerage` (FK) em todos os models relevantes
- Filtros automáticos por corretora no queryset de todas as views
- Mixins/middlewares que injetam a corretora do usuário logado
- Validação em nível de permissão para impedir acesso cruzado

```
┌─────────────────────────────────────────────────┐
│                   SCSI SaaS                     │
│                                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │Corretora │ │Corretora │ │Corretora │  ...    │
│  │    A     │ │    B     │ │    C     │        │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘        │
│       │             │             │              │
│       └─────────────┼─────────────┘              │
│                     │                            │
│            ┌────────▼────────┐                   │
│            │  SQLite (shared) │                   │
│            │  tenant filter   │                   │
│            └─────────────────┘                   │
└─────────────────────────────────────────────────┘
```

### 3.2 Hierarquia Operacional da Corretora

```
┌──────────────────────────────────────────────────────┐
│                    CORRETORA                         │
│              (Dono / Gerente / Admin)                │
│                                                      │
│    ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│    │ Agente A │  │ Agente B │  │ Agente C │  ...    │
│    │(PF ou PJ)│  │(PF ou PJ)│  │(PF ou PJ)│         │
│    └────┬─────┘  └────┬─────┘  └────┬─────┘         │
│         │              │              │               │
│    ┌────┴────┐    ┌────┴────┐    ┌────┴────┐         │
│    │Produtor1│    │Produtor3│    │Produtor5│         │
│    │Produtor2│    │Produtor4│    │         │         │
│    └─────────┘    └─────────┘    └─────────┘         │
│                                                      │
│    ┌───────────────────────┐                         │
│    │ Produtores Diretos    │  (sem agente)           │
│    │ Produtor6, Produtor7  │                         │
│    └───────────────────────┘                         │
└──────────────────────────────────────────────────────┘

Fluxo de Comissão:
Seguradora → Corretora → Agente → Produtor
                       └──────→ Produtor (direto)
```

### 3.3 Estrutura de Apps Django

```
scsi/
├── core/                    # Projeto Django (settings, urls, wsgi)
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── shared/                    # Mixins, middleware, utils compartilhados
├── design_system/
│   └── design-system.html   # Referência visual do design system
├── accounts/                # Autenticação, usuários, permissões e grupos
├── brokerages/              # Cadastro e gestão de corretoras (tenant)
├── agents/                  # Cadastro de agentes e produtores
├── plans/                   # Planos SaaS, assinaturas e billing
├── clients/                 # Cadastro de clientes (segurados)
├── insurers/                # Cadastro de seguradoras
├── branches/                # Ramos de seguro (CRUD)
├── policies/                # Apólices de seguro
├── proposals/               # Propostas de seguro
├── insured_items/           # Itens segurados (bens cobertos)
├── deals/                   # Negociações / CRM
├── claims/                  # Sinistros
├── endorsements/            # Endossos de apólices
├── renewals/                # Gestão de renovações
├── coverages/               # Coberturas e itens de cobertura
├── commissions/             # Gestão de comissões e repasses
├── reports/                 # Relatórios diversos
├── dashboard/               # Dashboard com métricas e KPIs
├── ai_agent/                # Agente de IA (LangChain/LangGraph)
├── landing/                 # Landing page pública do SaaS
├── templates/               # Templates globais e base
├── static/                  # Assets estáticos globais
├── manage.py
├── .env                     # Variáveis de ambiente
└── requirements.txt
```

---

## 4. Módulos e Funcionalidades

### 4.1 Landing Page (`landing`)

**Descrição:** Página pública principal do SaaS, acessível sem autenticação.

**Funcionalidades:**

- Hero section com copy de vendas focada em gestão inteligente e IA integrada
- Seção de funcionalidades/benefícios do sistema
- Seção de destaque para IA integrada e gestão inteligente
- Seção de planos e preços (valores por usuário)
- Seção de FAQ
- Seção de depoimentos/prova social
- CTA para criar conta / experimentar grátis
- Footer com informações institucionais
- Link para tela de login
- Link para tela de registro/onboarding

**Rotas:**

| Rota | View | Descrição |
|---|---|---|
| `/` | `LandingPageView` | Página principal pública |

---

### 4.2 Autenticação e Usuários (`accounts`)

**Descrição:** Sistema de autenticação customizado usando o sistema nativo do Django com login via email.

**Models:**

#### `User` (AbstractUser customizado)

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `email` | EmailField | Sim | Login principal (unique) |
| `first_name` | CharField | Sim | Nome |
| `last_name` | CharField | Sim | Sobrenome |
| `phone` | CharField | Não | Telefone |
| `cpf` | CharField | Não | CPF |
| `role` | CharField (choices) | Sim | Papel: `admin`, `owner`, `manager`, `agent`, `producer` |
| `is_active` | BooleanField | Sim | Ativo/Inativo |
| `avatar` | ImageField | Não | Foto do usuário |
| `created_at` | DateTimeField | Auto | Data de criação |
| `updated_at` | DateTimeField | Auto | Data de atualização |

- `USERNAME_FIELD = 'email'`
- `REQUIRED_FIELDS = ['first_name', 'last_name']`

#### `UserBrokerage` (M2M intermediária)

| Campo | Tipo | Descrição |
|---|---|---|
| `user` | FK(User) | Usuário |
| `brokerage` | FK(Brokerage) | Corretora |
| `is_default` | BooleanField | Corretora padrão do usuário |
| `joined_at` | DateTimeField | Data de vínculo |
| `created_at` | DateTimeField | Data de criação |
| `updated_at` | DateTimeField | Data de atualização |

**Funcionalidades:**

- Login via email + senha
- Registro de novo usuário com criação de corretora (onboarding)
- Recuperação de senha por email
- Gestão de perfil do usuário
- Gestão de permissões modulares e granulares (usando `Permission` nativo do Django)
- Criação e gestão de grupos de permissões (`Group` nativo do Django)
- Um usuário pode pertencer a múltiplas corretoras
- Seleção de corretora ativa na sessão (para usuários multi-corretora)

**Papéis (roles):**

| Role | Descrição | Escopo de dados |
|---|---|---|
| `admin` | Administrador do sistema (superuser) | Todos os dados de todas as corretoras |
| `owner` | Dono da corretora | Todos os dados da sua corretora |
| `manager` | Gerente da corretora | Todos os dados da sua corretora |
| `agent` | Agente da corretora | Dados dos seus produtores e negócios próprios |
| `producer` | Produtor/Corretor final | Apenas dados vinculados a ele |

**Rotas:**

| Rota | View | Descrição |
|---|---|---|
| `/accounts/login/` | `LoginView` | Tela de login |
| `/accounts/logout/` | `LogoutView` | Logout |
| `/accounts/register/` | `RegisterView` | Registro + onboarding |
| `/accounts/password-reset/` | `PasswordResetView` | Recuperação de senha |
| `/accounts/profile/` | `ProfileView` | Perfil do usuário |
| `/accounts/users/` | `UserListView` | Listagem de usuários da corretora |
| `/accounts/users/<pk>/` | `UserDetailView` | Detalhe/edição de usuário |
| `/accounts/users/create/` | `UserCreateView` | Criar novo usuário |
| `/accounts/groups/` | `GroupListView` | Listagem de grupos |
| `/accounts/groups/create/` | `GroupCreateView` | Criar grupo de permissões |
| `/accounts/groups/<pk>/` | `GroupDetailView` | Detalhe/edição de grupo |
| `/accounts/switch-brokerage/` | `SwitchBrokerageView` | Trocar corretora ativa |

---

### 4.3 Corretoras (`brokerages`)

**Descrição:** Cadastro e gestão das corretoras (tenants do sistema).

**Models:**

#### `Brokerage`

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `cnpj` | CharField | Sim | CNPJ da corretora (unique) |
| `legal_name` | CharField | Sim | Razão social |
| `trade_name` | CharField | Não | Nome fantasia |
| `susep_code` | CharField | Não | Código SUSEP |
| `email` | EmailField | Não | Email da corretora |
| `phone` | CharField | Não | Telefone |
| `address` | CharField | Não | Endereço completo |
| `city` | CharField | Não | Cidade |
| `state` | CharField | Não | Estado (UF) |
| `zip_code` | CharField | Não | CEP |
| `logo` | ImageField | Não | Logo da corretora |
| `status` | CharField (choices) | Sim | Status: `active`, `inactive`, `pending_payment`, `overdue` |
| `plan` | FK(Plan) | Não | Plano atual |
| `default_commission_rate` | DecimalField | Não | % de comissão padrão da corretora |
| `created_at` | DateTimeField | Auto | Data de criação |
| `updated_at` | DateTimeField | Auto | Data de atualização |

**Status possíveis:**

- `active` — Ativo
- `inactive` — Inativo
- `pending_payment` — Pagamento pendente
- `overdue` — Pagamento em atraso

**Administração:**

- Gerenciado pelo admin do Django (apenas superusers)
- CRUD de corretoras no Django Admin
- Controle de status, plano, ativação e módulos disponíveis

---

### 4.4 Agentes e Produtores (`agents`)

**Descrição:** Gestão da hierarquia comercial da corretora: agentes (intermediários) e produtores (corretores finais).

**Conceitos:**

- **Agente:** Pessoa física ou jurídica parceira que vende seguros para a corretora. Um agente pode ter vários produtores vinculados.
- **Produtor:** O corretor final que efetivamente realiza a venda. Pode estar vinculado a um agente ou trabalhar diretamente para a corretora.
- A comissão é paga pela seguradora à corretora, que repassa a parte correspondente ao agente e ao produtor.

**Models:**

#### `Agent`

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `brokerage` | FK(Brokerage) | Sim | Corretora (tenant) |
| `agent_type` | CharField (choices) | Sim | `individual` (PF) ou `company` (PJ) |
| `name` | CharField | Sim | Nome completo / Razão social |
| `cpf_cnpj` | CharField | Sim | CPF ou CNPJ |
| `susep_code` | CharField | Não | Código SUSEP |
| `email` | EmailField | Não | Email |
| `phone` | CharField | Não | Telefone |
| `address` | CharField | Não | Endereço |
| `city` | CharField | Não | Cidade |
| `state` | CharField | Não | Estado (UF) |
| `zip_code` | CharField | Não | CEP |
| `commission_rate` | DecimalField | Não | % de comissão padrão do agente |
| `user` | OneToOneField(User, null=True) | Não | Usuário vinculado (para acesso ao sistema) |
| `notes` | TextField | Não | Observações |
| `is_active` | BooleanField | Sim | Ativo/Inativo |
| `created_at` | DateTimeField | Auto | Data de criação |
| `updated_at` | DateTimeField | Auto | Data de atualização |

#### `Producer`

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `brokerage` | FK(Brokerage) | Sim | Corretora (tenant) |
| `agent` | FK(Agent, null=True, blank=True) | Não | Agente vinculado (null = produtor direto da corretora) |
| `name` | CharField | Sim | Nome completo |
| `cpf` | CharField | Sim | CPF |
| `susep_code` | CharField | Não | Código SUSEP |
| `email` | EmailField | Não | Email |
| `phone` | CharField | Não | Telefone |
| `commission_rate` | DecimalField | Não | % de comissão padrão do produtor |
| `user` | OneToOneField(User, null=True) | Não | Usuário vinculado (para acesso ao sistema) |
| `notes` | TextField | Não | Observações |
| `is_active` | BooleanField | Sim | Ativo/Inativo |
| `created_at` | DateTimeField | Auto | Data de criação |
| `updated_at` | DateTimeField | Auto | Data de atualização |

**Regras de Negócio:**

- Um `Agent` pode ter 0 ou N `Producer` vinculados
- Um `Producer` pode ter 0 ou 1 `Agent` (null = vinculado diretamente à corretora)
- Um `Agent` ou `Producer` pode opcionalmente estar vinculado a um `User` para acesso ao sistema
- Quando vinculado a um `User`, o role do usuário deve ser `agent` ou `producer` respectivamente

**Funcionalidades:**

- CRUD completo de agentes
- CRUD completo de produtores
- Vinculação de produtores a agentes
- Configuração de % de comissão padrão por agente e produtor
- Listagem de produtores por agente

**Rotas:**

| Rota | View | Descrição |
|---|---|---|
| `/agents/` | `AgentListView` | Listagem de agentes |
| `/agents/create/` | `AgentCreateView` | Criar agente |
| `/agents/<pk>/` | `AgentDetailView` | Detalhe do agente |
| `/agents/<pk>/edit/` | `AgentUpdateView` | Editar agente |
| `/agents/<pk>/delete/` | `AgentDeleteView` | Excluir agente |
| `/producers/` | `ProducerListView` | Listagem de produtores |
| `/producers/create/` | `ProducerCreateView` | Criar produtor |
| `/producers/<pk>/` | `ProducerDetailView` | Detalhe do produtor |
| `/producers/<pk>/edit/` | `ProducerUpdateView` | Editar produtor |
| `/producers/<pk>/delete/` | `ProducerDeleteView` | Excluir produtor |

---

### 4.5 Planos e Assinaturas (`plans`)

**Descrição:** Gestão de planos SaaS, assinaturas e controle de billing.

**Models:**

#### `Plan`

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `name` | CharField | Sim | Nome do plano |
| `slug` | SlugField | Sim | Slug único |
| `description` | TextField | Não | Descrição do plano |
| `price_per_user` | DecimalField | Sim | Valor mensal por usuário |
| `max_users` | IntegerField | Não | Limite de usuários (null = ilimitado) |
| `features` | JSONField | Não | Lista de funcionalidades inclusas |
| `is_free` | BooleanField | Sim | Se é o plano gratuito |
| `is_active` | BooleanField | Sim | Se o plano está disponível |
| `created_at` | DateTimeField | Auto | Data de criação |
| `updated_at` | DateTimeField | Auto | Data de atualização |

#### `Subscription`

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `brokerage` | FK(Brokerage) | Sim | Corretora |
| `plan` | FK(Plan) | Sim | Plano assinado |
| `status` | CharField (choices) | Sim | `active`, `cancelled`, `suspended` |
| `started_at` | DateTimeField | Sim | Início da assinatura |
| `expires_at` | DateTimeField | Não | Data de expiração |
| `created_at` | DateTimeField | Auto | Data de criação |
| `updated_at` | DateTimeField | Auto | Data de atualização |

#### `Payment`

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `subscription` | FK(Subscription) | Sim | Assinatura relacionada |
| `amount` | DecimalField | Sim | Valor pago |
| `payment_date` | DateTimeField | Sim | Data do pagamento |
| `status` | CharField (choices) | Sim | `paid`, `pending`, `failed`, `refunded` |
| `reference` | CharField | Não | Referência/ID do pagamento |
| `created_at` | DateTimeField | Auto | Data de criação |
| `updated_at` | DateTimeField | Auto | Data de atualização |

**Administração:**

- Planos, assinaturas e pagamentos gerenciados pelo Django Admin
- Administradores podem ativar/desativar planos e módulos por corretora

---

### 4.6 Clientes (`clients`)

**Descrição:** Cadastro de clientes (segurados) da corretora.

**Models:**

#### `Client`

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `brokerage` | FK(Brokerage) | Sim | Corretora (tenant) |
| `client_type` | CharField (choices) | Sim | `individual` (PF) ou `company` (PJ) |
| `name` | CharField | Sim | Nome completo / Razão social |
| `cpf_cnpj` | CharField | Sim | CPF ou CNPJ |
| `email` | EmailField | Não | Email |
| `phone` | CharField | Não | Telefone principal |
| `secondary_phone` | CharField | Não | Telefone secundário |
| `birth_date` | DateField | Não | Data de nascimento |
| `address` | CharField | Não | Endereço |
| `city` | CharField | Não | Cidade |
| `state` | CharField | Não | Estado (UF) |
| `zip_code` | CharField | Não | CEP |
| `notes` | TextField | Não | Observações |
| `is_active` | BooleanField | Sim | Ativo/Inativo |
| `assigned_producer` | FK(Producer, null=True) | Não | Produtor responsável |
| `created_at` | DateTimeField | Auto | Data de criação |
| `updated_at` | DateTimeField | Auto | Data de atualização |

**Funcionalidades:**

- CRUD completo de clientes
- Filtro por tipo (PF/PJ), status, produtor responsável
- Busca por nome, CPF/CNPJ, email
- Botão "Resumir com IA" no detalhe do cliente
- Exibição do último resumo IA gerado no registro do cliente

**Rotas:**

| Rota | View | Descrição |
|---|---|---|
| `/clients/` | `ClientListView` | Listagem de clientes |
| `/clients/create/` | `ClientCreateView` | Criar cliente |
| `/clients/<pk>/` | `ClientDetailView` | Detalhe do cliente |
| `/clients/<pk>/edit/` | `ClientUpdateView` | Editar cliente |
| `/clients/<pk>/delete/` | `ClientDeleteView` | Excluir cliente |

---

### 4.7 Seguradoras (`insurers`)

**Descrição:** Cadastro de seguradoras parceiras.

**Models:**

#### `Insurer`

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `brokerage` | FK(Brokerage) | Sim | Corretora (tenant) |
| `name` | CharField | Sim | Nome da seguradora |
| `cnpj` | CharField | Não | CNPJ |
| `susep_code` | CharField | Não | Código SUSEP |
| `email` | EmailField | Não | Email |
| `phone` | CharField | Não | Telefone |
| `website` | URLField | Não | Site |
| `contact_name` | CharField | Não | Nome do contato |
| `notes` | TextField | Não | Observações |
| `is_active` | BooleanField | Sim | Ativo/Inativo |
| `created_at` | DateTimeField | Auto | Data de criação |
| `updated_at` | DateTimeField | Auto | Data de atualização |

**Funcionalidades:**

- CRUD completo de seguradoras
- Filtro e busca

**Rotas:**

| Rota | View | Descrição |
|---|---|---|
| `/insurers/` | `InsurerListView` | Listagem |
| `/insurers/create/` | `InsurerCreateView` | Criar |
| `/insurers/<pk>/` | `InsurerDetailView` | Detalhe |
| `/insurers/<pk>/edit/` | `InsurerUpdateView` | Editar |
| `/insurers/<pk>/delete/` | `InsurerDeleteView` | Excluir |

---

### 4.8 Ramos de Seguro (`branches`)

**Descrição:** Cadastro e gestão de ramos de seguro como entidade independente, referenciada por propostas, apólices, coberturas e negociações.

**Models:**

#### `InsuranceBranch`

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `brokerage` | FK(Brokerage) | Sim | Corretora (tenant) |
| `name` | CharField | Sim | Nome do ramo (ex: Automóvel, Vida, Residencial, Empresarial, Transporte, Viagem, Saúde, Responsabilidade Civil) |
| `code` | CharField | Não | Código do ramo (referência SUSEP) |
| `description` | TextField | Não | Descrição do ramo |
| `is_active` | BooleanField | Sim | Ativo/Inativo |
| `created_at` | DateTimeField | Auto | Data de criação |
| `updated_at` | DateTimeField | Auto | Data de atualização |

**Ramos padrão (seed/fixture):**

| Nome | Código | Descrição |
|---|---|---|
| Automóvel | 0531 | Seguro de veículos automotores |
| Vida Individual | 0977 | Seguro de vida individual |
| Vida em Grupo | 0993 | Seguro de vida coletivo/grupo |
| Residencial | 0114 | Seguro residencial |
| Empresarial | 0141 | Seguro empresarial/patrimonial |
| Transporte | 0621 | Seguro de transporte de cargas |
| Viagem | 1369 | Seguro viagem nacional/internacional |
| Saúde | 1066 | Seguro saúde |
| Responsabilidade Civil | 0351 | RC geral/profissional |
| Garantia | 0775 | Seguro garantia |
| Riscos de Engenharia | 0167 | Seguro para obras e instalações |
| Condomínio | 0114 | Seguro condomínio |
| Frota | 0531 | Seguro de frota de veículos |
| Agrícola | 0116 | Seguro agrícola |
| Previdência | 0994 | Planos de previdência privada |

**Funcionalidades:**

- CRUD completo de ramos
- Ramos pré-cadastrados por fixture para novas corretoras
- Busca e filtro
- Ramo é referenciado como FK por: `Proposal`, `Policy`, `Deal`, `CoverageType`

**Rotas:**

| Rota | View | Descrição |
|---|---|---|
| `/branches/` | `InsuranceBranchListView` | Listagem |
| `/branches/create/` | `InsuranceBranchCreateView` | Criar |
| `/branches/<pk>/` | `InsuranceBranchDetailView` | Detalhe |
| `/branches/<pk>/edit/` | `InsuranceBranchUpdateView` | Editar |
| `/branches/<pk>/delete/` | `InsuranceBranchDeleteView` | Excluir |

**Impacto em outros models:**

Todos os campos `insurance_branch` nos models `Proposal`, `Policy`, `Deal` e `CoverageType` são FK para `branches.InsuranceBranch`:

```python
insurance_branch = models.ForeignKey(
    'branches.InsuranceBranch',
    on_delete=models.PROTECT,
    related_name='...',
    verbose_name='Ramo de Seguro'
)
```

---

### 4.9 Coberturas (`coverages`)

**Descrição:** Gestão de tipos de cobertura e itens de cobertura vinculados a apólices.

**Models:**

#### `CoverageType`

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `brokerage` | FK(Brokerage) | Sim | Corretora (tenant) |
| `name` | CharField | Sim | Nome da cobertura (ex: incêndio, roubo, RCF, colisão) |
| `description` | TextField | Não | Descrição |
| `insurance_branch` | FK(InsuranceBranch) | Não | Ramo de seguro vinculado |
| `is_active` | BooleanField | Sim | Ativo/Inativo |
| `created_at` | DateTimeField | Auto | Data de criação |
| `updated_at` | DateTimeField | Auto | Data de atualização |

#### `CoverageItem`

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `policy` | FK(Policy) | Sim | Apólice vinculada |
| `insured_item` | FK(InsuredItem, null=True) | Não | Item segurado vinculado |
| `coverage_type` | FK(CoverageType) | Sim | Tipo de cobertura |
| `insured_amount` | DecimalField | Sim | Valor segurado (IS) |
| `deductible` | DecimalField | Não | Franquia |
| `premium` | DecimalField | Não | Prêmio da cobertura |
| `notes` | TextField | Não | Observações |
| `created_at` | DateTimeField | Auto | Data de criação |
| `updated_at` | DateTimeField | Auto | Data de atualização |

**Funcionalidades:**

- CRUD de tipos de cobertura
- Vinculação de coberturas a apólices com valores (IS, franquia, prêmio)
- Vinculação opcional de cobertura a item segurado específico
- Gestão inline de coberturas dentro do formulário da apólice

---

### 4.10 Itens Segurados (`insured_items`)

**Descrição:** Entidade que representa os bens, objetos ou sujeitos cobertos por uma proposta ou apólice. Cada apólice/proposta pode ter múltiplos itens segurados. Sinistros são sempre vinculados a um item segurado específico.

**Exemplos de itens segurados:**

- Um automóvel (marca, modelo, placa, chassi)
- Um imóvel residencial (endereço)
- Um item de frota (veículo específico dentro de uma frota)
- Uma viagem (destino, datas)
- Uma vida (dados do segurado)
- Um equipamento (descrição, número de série)
- Um imóvel empresarial (endereço, tipo de atividade)

**Models:**

#### `InsuredItem`

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `brokerage` | FK(Brokerage) | Sim | Corretora (tenant) |
| `proposal` | FK(Proposal, null=True, blank=True) | Não | Proposta vinculada |
| `policy` | FK(Policy, null=True, blank=True) | Não | Apólice vinculada |
| `item_type` | CharField (choices) | Sim | Tipo do item (ver tabela abaixo) |
| `description` | CharField | Sim | Descrição principal do item (ex: "Honda Civic 2024 Placa ABC-1234") |
| `insured_amount` | DecimalField | Não | Valor segurado do item (IS) |
| `details` | JSONField | Não | Dados específicos do item em formato JSON (ver estrutura abaixo) |
| `notes` | TextField | Não | Observações |
| `order` | IntegerField | Não | Ordem do item na listagem |
| `created_at` | DateTimeField | Auto | Data de criação |
| `updated_at` | DateTimeField | Auto | Data de atualização |

**Tipos de item (`item_type`):**

| Valor | Label | Campos típicos no `details` (JSON) |
|---|---|---|
| `vehicle` | Veículo | `brand`, `model`, `year`, `plate`, `chassis`, `renavam`, `color`, `fuel_type`, `fipe_code` |
| `property` | Imóvel | `address`, `city`, `state`, `zip_code`, `property_type` (casa, apto, comercial), `area_sqm`, `construction_year` |
| `life` | Vida | `insured_name`, `cpf`, `birth_date`, `occupation`, `capital` |
| `travel` | Viagem | `destination`, `departure_date`, `return_date`, `travelers_count`, `traveler_names` |
| `fleet_vehicle` | Veículo de Frota | `brand`, `model`, `year`, `plate`, `chassis`, `fleet_id` |
| `equipment` | Equipamento | `equipment_name`, `serial_number`, `brand`, `model`, `acquisition_value` |
| `cargo` | Carga/Transporte | `cargo_description`, `origin`, `destination`, `transport_mode`, `invoice_value` |
| `other` | Outro | Campos livres no JSON |

**Regras de Negócio:**

- Um `InsuredItem` deve estar vinculado a pelo menos uma `Proposal` ou `Policy` (validação no form/view)
- Ao converter proposta em apólice, os itens segurados da proposta são copiados/vinculados à nova apólice
- Um sinistro (`Claim`) é sempre vinculado a um `InsuredItem` específico
- Cada `Proposal` e `Policy` pode ter 1 ou N itens segurados
- Coberturas (`CoverageItem`) podem ser vinculadas a um item segurado específico

**Funcionalidades:**

- Gestão inline de itens segurados dentro dos formulários de proposta e apólice
- Formulário dinâmico que exibe campos específicos por `item_type`
- Listagem de itens segurados por apólice/proposta
- Busca de itens (ex: buscar por placa, endereço)

**Rotas:**

Itens segurados são gerenciados inline dentro de propostas e apólices. Rotas auxiliares:

| Rota | View | Descrição |
|---|---|---|
| `/insured-items/<pk>/` | `InsuredItemDetailView` | Detalhe do item segurado |
| `/insured-items/<pk>/edit/` | `InsuredItemUpdateView` | Editar item segurado |

---

### 4.11 Propostas (`proposals`)

**Descrição:** Gestão de propostas de seguro antes da emissão da apólice.

**Models:**

#### `Proposal`

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `brokerage` | FK(Brokerage) | Sim | Corretora (tenant) |
| `proposal_number` | CharField | Sim | Número da proposta |
| `client` | FK(Client) | Sim | Cliente |
| `insurer` | FK(Insurer) | Sim | Seguradora |
| `insurance_branch` | FK(InsuranceBranch) | Sim | Ramo de seguro |
| `producer` | FK(Producer) | Sim | Produtor responsável |
| `agent` | FK(Agent, null=True) | Não | Agente vinculado (herdado do produtor ou manual) |
| `status` | CharField (choices) | Sim | Ver tabela abaixo |
| `start_date` | DateField | Não | Início da vigência proposta |
| `end_date` | DateField | Não | Fim da vigência proposta |
| `total_premium` | DecimalField | Não | Prêmio total |
| `commission_rate` | DecimalField | Não | Percentual de comissão da corretora |
| `commission_value` | DecimalField | Não | Valor da comissão da corretora |
| `notes` | TextField | Não | Observações |
| `created_at` | DateTimeField | Auto | Data de criação |
| `updated_at` | DateTimeField | Auto | Data de atualização |

**Relações:**

- `InsuredItem` → FK(Proposal) — múltiplos itens segurados por proposta

**Status da proposta:**

- `draft` — Rascunho
- `submitted` — Enviada à seguradora
- `under_analysis` — Em análise
- `approved` — Aprovada
- `rejected` — Recusada
- `issued` — Emitida (gerou apólice)
- `cancelled` — Cancelada

**Funcionalidades:**

- CRUD completo
- Gestão inline de itens segurados
- Conversão de proposta aprovada para apólice (com cópia dos itens segurados)
- Botão "Resumir com IA" no detalhe
- Exibição do último resumo IA no registro

**Rotas:**

| Rota | View | Descrição |
|---|---|---|
| `/proposals/` | `ProposalListView` | Listagem |
| `/proposals/create/` | `ProposalCreateView` | Criar |
| `/proposals/<pk>/` | `ProposalDetailView` | Detalhe |
| `/proposals/<pk>/edit/` | `ProposalUpdateView` | Editar |
| `/proposals/<pk>/delete/` | `ProposalDeleteView` | Excluir |
| `/proposals/<pk>/convert/` | `ProposalConvertView` | Converter em apólice |

---

### 4.12 Apólices (`policies`)

**Descrição:** Gestão de apólices de seguro emitidas.

**Models:**

#### `Policy`

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `brokerage` | FK(Brokerage) | Sim | Corretora (tenant) |
| `policy_number` | CharField | Sim | Número da apólice |
| `proposal` | FK(Proposal) | Não | Proposta de origem |
| `client` | FK(Client) | Sim | Cliente (segurado) |
| `insurer` | FK(Insurer) | Sim | Seguradora |
| `insurance_branch` | FK(InsuranceBranch) | Sim | Ramo de seguro |
| `producer` | FK(Producer) | Sim | Produtor responsável |
| `agent` | FK(Agent, null=True) | Não | Agente vinculado |
| `status` | CharField (choices) | Sim | Ver tabela abaixo |
| `start_date` | DateField | Sim | Início da vigência |
| `end_date` | DateField | Sim | Fim da vigência |
| `total_premium` | DecimalField | Sim | Prêmio total |
| `insured_amount` | DecimalField | Não | Importância segurada total |
| `commission_rate` | DecimalField | Não | % de comissão da corretora |
| `commission_value` | DecimalField | Não | Valor da comissão da corretora |
| `installments` | IntegerField | Não | Número de parcelas |
| `notes` | TextField | Não | Observações |
| `created_at` | DateTimeField | Auto | Data de criação |
| `updated_at` | DateTimeField | Auto | Data de atualização |

**Relações:**

- `InsuredItem` → FK(Policy) — múltiplos itens segurados por apólice
- `CoverageItem` → FK(Policy) — múltiplas coberturas por apólice

**Status da apólice:**

- `active` — Vigente
- `expired` — Vencida
- `cancelled` — Cancelada
- `renewed` — Renovada
- `suspended` — Suspensa

**Funcionalidades:**

- CRUD completo
- Gestão inline de itens segurados
- Coberturas vinculadas (inline via `CoverageItem`)
- Cálculo automático de comissão
- Controle de vigência
- Botão "Resumir com IA" no detalhe
- Exibição do último resumo IA no registro

**Rotas:**

| Rota | View | Descrição |
|---|---|---|
| `/policies/` | `PolicyListView` | Listagem |
| `/policies/create/` | `PolicyCreateView` | Criar |
| `/policies/<pk>/` | `PolicyDetailView` | Detalhe |
| `/policies/<pk>/edit/` | `PolicyUpdateView` | Editar |
| `/policies/<pk>/delete/` | `PolicyDeleteView` | Excluir |

---

### 4.13 Sinistros (`claims`)

**Descrição:** Gestão de sinistros reportados pelos clientes. Um sinistro é sempre vinculado a um item segurado específico de uma apólice.

**Models:**

#### `Claim`

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `brokerage` | FK(Brokerage) | Sim | Corretora (tenant) |
| `claim_number` | CharField | Sim | Número do sinistro |
| `policy` | FK(Policy) | Sim | Apólice vinculada |
| `insured_item` | FK(InsuredItem) | Sim | Item segurado sinistrado |
| `client` | FK(Client) | Sim | Cliente |
| `insurer` | FK(Insurer) | Sim | Seguradora |
| `occurrence_date` | DateField | Sim | Data da ocorrência |
| `report_date` | DateField | Sim | Data da comunicação |
| `status` | CharField (choices) | Sim | Ver tabela abaixo |
| `description` | TextField | Sim | Descrição do sinistro |
| `claimed_amount` | DecimalField | Não | Valor reclamado |
| `approved_amount` | DecimalField | Não | Valor aprovado/indenizado |
| `resolution_date` | DateField | Não | Data da resolução |
| `notes` | TextField | Não | Observações |
| `created_at` | DateTimeField | Auto | Data de criação |
| `updated_at` | DateTimeField | Auto | Data de atualização |

**Regras de Negócio:**

- O `insured_item` deve pertencer à `policy` selecionada (validação)
- Ao selecionar a apólice, os itens segurados disponíveis são filtrados automaticamente
- O `client` e `insurer` são herdados/validados a partir da apólice

**Status do sinistro:**

- `reported` — Comunicado
- `under_analysis` — Em análise
- `documentation_pending` — Aguardando documentação
- `approved` — Aprovado
- `denied` — Negado
- `paid` — Indenizado/Pago
- `closed` — Encerrado

**Funcionalidades:**

- CRUD completo
- Seleção de item segurado vinculado à apólice
- Timeline de status
- Botão "Resumir com IA" no detalhe
- Exibição do último resumo IA no registro

**Rotas:**

| Rota | View | Descrição |
|---|---|---|
| `/claims/` | `ClaimListView` | Listagem |
| `/claims/create/` | `ClaimCreateView` | Criar |
| `/claims/<pk>/` | `ClaimDetailView` | Detalhe |
| `/claims/<pk>/edit/` | `ClaimUpdateView` | Editar |
| `/claims/<pk>/delete/` | `ClaimDeleteView` | Excluir |

---

### 4.14 Endossos (`endorsements`)

**Descrição:** Gestão de endossos (alterações) em apólices vigentes.

**Models:**

#### `Endorsement`

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `brokerage` | FK(Brokerage) | Sim | Corretora (tenant) |
| `policy` | FK(Policy) | Sim | Apólice vinculada |
| `endorsement_number` | CharField | Sim | Número do endosso |
| `endorsement_type` | CharField (choices) | Sim | `inclusion`, `exclusion`, `alteration`, `cancellation` |
| `description` | TextField | Sim | Descrição da alteração |
| `effective_date` | DateField | Sim | Data de vigência do endosso |
| `premium_difference` | DecimalField | Não | Diferença de prêmio |
| `status` | CharField (choices) | Sim | `pending`, `approved`, `rejected`, `applied` |
| `notes` | TextField | Não | Observações |
| `created_at` | DateTimeField | Auto | Data de criação |
| `updated_at` | DateTimeField | Auto | Data de atualização |

**Funcionalidades:**

- CRUD completo
- Vínculo obrigatório com apólice
- Registro de diferença de prêmio

**Rotas:**

| Rota | View | Descrição |
|---|---|---|
| `/endorsements/` | `EndorsementListView` | Listagem |
| `/endorsements/create/` | `EndorsementCreateView` | Criar |
| `/endorsements/<pk>/` | `EndorsementDetailView` | Detalhe |
| `/endorsements/<pk>/edit/` | `EndorsementUpdateView` | Editar |

---

### 4.15 Renovações (`renewals`)

**Descrição:** Gestão e acompanhamento de renovações de apólices.

**Models:**

#### `Renewal`

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `brokerage` | FK(Brokerage) | Sim | Corretora (tenant) |
| `original_policy` | FK(Policy, related_name='renewals') | Sim | Apólice original |
| `renewed_policy` | FK(Policy, related_name='renewed_from', null=True) | Não | Nova apólice (se renovada) |
| `status` | CharField (choices) | Sim | `pending`, `in_progress`, `renewed`, `not_renewed`, `lost` |
| `due_date` | DateField | Sim | Data de vencimento para renovação |
| `contacted_at` | DateTimeField | Não | Data do contato com o cliente |
| `notes` | TextField | Não | Observações |
| `assigned_producer` | FK(Producer) | Não | Produtor responsável |
| `created_at` | DateTimeField | Auto | Data de criação |
| `updated_at` | DateTimeField | Auto | Data de atualização |

**Funcionalidades:**

- Listagem de apólices próximas ao vencimento
- Fluxo de renovação (contato → proposta → nova apólice)
- Alertas de prazo
- Relatório de taxa de renovação

**Rotas:**

| Rota | View | Descrição |
|---|---|---|
| `/renewals/` | `RenewalListView` | Listagem |
| `/renewals/<pk>/` | `RenewalDetailView` | Detalhe |
| `/renewals/<pk>/edit/` | `RenewalUpdateView` | Editar |

---

### 4.16 Negociações / CRM (`deals`)

**Descrição:** Painel CRM para corretores gerenciarem negociações de seguros com visão grid e kanban.

**Models:**

#### `DealStage`

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `brokerage` | FK(Brokerage) | Sim | Corretora (tenant) |
| `name` | CharField | Sim | Nome do estágio |
| `order` | IntegerField | Sim | Ordem no pipeline |
| `color` | CharField | Não | Cor do estágio (hex) |
| `is_won` | BooleanField | Sim | Se representa negócio ganho |
| `is_lost` | BooleanField | Sim | Se representa negócio perdido |
| `created_at` | DateTimeField | Auto | Data de criação |
| `updated_at` | DateTimeField | Auto | Data de atualização |

**Estágios padrão (seed):**

1. Prospecção
2. Contato Realizado
3. Cotação Enviada
4. Negociação
5. Proposta Aceita
6. Ganho ✓
7. Perdido ✗

#### `Deal`

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `brokerage` | FK(Brokerage) | Sim | Corretora (tenant) |
| `title` | CharField | Sim | Título do negócio |
| `client` | FK(Client) | Sim | Cliente |
| `producer` | FK(Producer) | Sim | Produtor responsável |
| `agent` | FK(Agent, null=True) | Não | Agente vinculado |
| `stage` | FK(DealStage) | Sim | Estágio atual |
| `insurer` | FK(Insurer) | Não | Seguradora |
| `insurance_branch` | FK(InsuranceBranch) | Não | Ramo de seguro |
| `estimated_premium` | DecimalField | Não | Prêmio estimado |
| `estimated_commission` | DecimalField | Não | Comissão estimada |
| `probability` | IntegerField | Não | Probabilidade de fechamento (%) |
| `expected_close_date` | DateField | Não | Data prevista de fechamento |
| `proposal` | FK(Proposal) | Não | Proposta vinculada |
| `policy` | FK(Policy) | Não | Apólice vinculada |
| `lost_reason` | TextField | Não | Motivo da perda |
| `notes` | TextField | Não | Observações |
| `created_at` | DateTimeField | Auto | Data de criação |
| `updated_at` | DateTimeField | Auto | Data de atualização |

#### `DealActivity`

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `deal` | FK(Deal) | Sim | Negócio |
| `user` | FK(User) | Sim | Usuário que registrou |
| `activity_type` | CharField (choices) | Sim | `note`, `call`, `email`, `meeting`, `stage_change` |
| `description` | TextField | Sim | Descrição da atividade |
| `created_at` | DateTimeField | Auto | Data de criação |
| `updated_at` | DateTimeField | Auto | Data de atualização |

**Funcionalidades:**

- Visão Grid: tabela com filtros, ordenação e busca
- Visão Kanban: drag-and-drop entre estágios
- Registro de atividades por negócio
- Vinculação com proposta e apólice
- Botão "Resumir com IA" no detalhe do negócio
- Exibição do último resumo IA no registro
- Filtros por produtor, agente, estágio, ramo, seguradora

**Rotas:**

| Rota | View | Descrição |
|---|---|---|
| `/deals/` | `DealListView` | Visão Grid |
| `/deals/kanban/` | `DealKanbanView` | Visão Kanban |
| `/deals/create/` | `DealCreateView` | Criar negócio |
| `/deals/<pk>/` | `DealDetailView` | Detalhe |
| `/deals/<pk>/edit/` | `DealUpdateView` | Editar |
| `/deals/<pk>/delete/` | `DealDeleteView` | Excluir |
| `/deals/<pk>/activity/` | `DealActivityCreateView` | Registrar atividade |

---

### 4.17 Gestão de Comissões (`commissions`)

**Descrição:** Gestão completa de comissões recebidas pela corretora e repasses para agentes e produtores.

**Conceitos:**

```
Seguradora paga comissão à Corretora
         │
         ▼
┌─────────────────────────┐
│   Comissão da Corretora  │  (ex: 20% do prêmio = R$ 2.000)
│   commission_value       │
└────────┬────────────────┘
         │
         ├── Retenção Corretora: R$ 800 (40%)
         │
         ├── Repasse Agente: R$ 720 (36%)
         │   └── (% do agente sobre a comissão da corretora)
         │
         └── Repasse Produtor: R$ 480 (24%)
             └── (% do produtor sobre a comissão da corretora)
```

**Models:**

#### `CommissionRule`

Regra de comissão configurável por combinação de ramo, seguradora, agente e/ou produtor.

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `brokerage` | FK(Brokerage) | Sim | Corretora (tenant) |
| `name` | CharField | Sim | Nome/descrição da regra |
| `insurance_branch` | FK(InsuranceBranch, null=True) | Não | Ramo (null = todos os ramos) |
| `insurer` | FK(Insurer, null=True) | Não | Seguradora (null = todas) |
| `agent` | FK(Agent, null=True) | Não | Agente específico (null = todos) |
| `producer` | FK(Producer, null=True) | Não | Produtor específico (null = todos) |
| `brokerage_commission_rate` | DecimalField | Sim | % de comissão que a corretora recebe da seguradora |
| `agent_share_rate` | DecimalField | Não | % da comissão da corretora que vai para o agente |
| `producer_share_rate` | DecimalField | Não | % da comissão da corretora que vai para o produtor |
| `brokerage_retention_rate` | DecimalField | Sim | % da comissão que fica retida na corretora |
| `priority` | IntegerField | Sim | Prioridade da regra (maior = mais específica, prevalece) |
| `is_active` | BooleanField | Sim | Ativo/Inativo |
| `notes` | TextField | Não | Observações |
| `created_at` | DateTimeField | Auto | Data de criação |
| `updated_at` | DateTimeField | Auto | Data de atualização |

**Regras de resolução de comissão:**

1. Buscar regra mais específica (maior `priority`) que combina com ramo + seguradora + agente + produtor
2. Se não encontrar, buscar por ramo + seguradora
3. Se não encontrar, buscar por ramo
4. Se não encontrar, usar % padrão do agente/produtor/corretora

**Validação:** `agent_share_rate + producer_share_rate + brokerage_retention_rate = 100%`

#### `Commission`

Registro de comissão de uma apólice.

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `brokerage` | FK(Brokerage) | Sim | Corretora (tenant) |
| `policy` | FK(Policy) | Sim | Apólice vinculada |
| `rule_applied` | FK(CommissionRule, null=True) | Não | Regra aplicada |
| `total_premium` | DecimalField | Sim | Prêmio total da apólice |
| `commission_rate` | DecimalField | Sim | % de comissão recebida |
| `commission_value` | DecimalField | Sim | Valor total da comissão |
| `status` | CharField (choices) | Sim | `pending`, `received`, `partially_paid`, `paid`, `cancelled` |
| `received_date` | DateField | Não | Data de recebimento da seguradora |
| `notes` | TextField | Não | Observações |
| `created_at` | DateTimeField | Auto | Data de criação |
| `updated_at` | DateTimeField | Auto | Data de atualização |

**Status da comissão:**

- `pending` — Aguardando recebimento da seguradora
- `received` — Recebida pela corretora (repasses pendentes)
- `partially_paid` — Repasses parcialmente realizados
- `paid` — Todos os repasses realizados
- `cancelled` — Cancelada

#### `CommissionSplit`

Registro de cada repasse individual (para agente ou produtor).

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `commission` | FK(Commission) | Sim | Comissão pai |
| `recipient_type` | CharField (choices) | Sim | `brokerage_retention`, `agent`, `producer` |
| `agent` | FK(Agent, null=True) | Não | Agente (se recipient_type = agent) |
| `producer` | FK(Producer, null=True) | Não | Produtor (se recipient_type = producer) |
| `share_rate` | DecimalField | Sim | % sobre a comissão total |
| `share_value` | DecimalField | Sim | Valor do repasse |
| `status` | CharField (choices) | Sim | `pending`, `paid`, `cancelled` |
| `paid_date` | DateField | Não | Data do pagamento do repasse |
| `payment_reference` | CharField | Não | Referência do pagamento |
| `notes` | TextField | Não | Observações |
| `created_at` | DateTimeField | Auto | Data de criação |
| `updated_at` | DateTimeField | Auto | Data de atualização |

**Funcionalidades:**

- CRUD de regras de comissão
- Cálculo automático de comissão ao criar/editar apólice
- Geração automática de splits (repasses) ao registrar comissão
- Dashboard de comissões: recebidas, pendentes, a repassar
- Marcação de repasses como pagos
- Filtros por período, agente, produtor, ramo, seguradora
- Extrato de comissão por agente e por produtor

**Rotas:**

| Rota | View | Descrição |
|---|---|---|
| `/commissions/` | `CommissionListView` | Listagem de comissões |
| `/commissions/<pk>/` | `CommissionDetailView` | Detalhe da comissão + splits |
| `/commissions/rules/` | `CommissionRuleListView` | Listagem de regras |
| `/commissions/rules/create/` | `CommissionRuleCreateView` | Criar regra |
| `/commissions/rules/<pk>/` | `CommissionRuleDetailView` | Detalhe da regra |
| `/commissions/rules/<pk>/edit/` | `CommissionRuleUpdateView` | Editar regra |
| `/commissions/splits/` | `CommissionSplitListView` | Listagem de repasses |
| `/commissions/splits/<pk>/pay/` | `CommissionSplitPayView` | Marcar repasse como pago |
| `/commissions/agent-statement/<pk>/` | `AgentStatementView` | Extrato do agente |
| `/commissions/producer-statement/<pk>/` | `ProducerStatementView` | Extrato do produtor |

---

### 4.18 Dashboard (`dashboard`)

**Descrição:** Tela principal após login com visão geral e métricas da corretora.

**Métricas e KPIs:**

| Métrica | Descrição |
|---|---|
| Total de Clientes | Clientes ativos da corretora |
| Apólices Vigentes | Apólices com status `active` |
| Prêmio Total em Carteira | Soma dos prêmios de apólices vigentes |
| Comissão Total | Soma das comissões de apólices vigentes |
| Comissões Pendentes | Comissões aguardando recebimento |
| Repasses Pendentes | Splits com status `pending` |
| Renovações Pendentes | Apólices a vencer nos próximos 30/60/90 dias |
| Sinistros Abertos | Sinistros com status em andamento |
| Negócios no Pipeline | Total de deals abertos |
| Valor Estimado no Pipeline | Soma dos prêmios estimados dos deals |
| Taxa de Conversão | Negócios ganhos / total de negócios |
| Top Seguradoras | Ranking por volume de prêmio |
| Top Ramos | Ranking de ramos por prêmio |
| Distribuição por Produtor | Carteira por produtor |
| Distribuição por Agente | Carteira por agente |
| Comissão por Agente/Produtor | Ranking de comissões |

**Componentes visuais:**

- Cards de KPIs no topo
- Componente acordeão no topo com insight geral do agente de IA
- Gráficos de barras, linhas e pizza (chart.js ou similar)
- Tabela de renovações próximas
- Mini-kanban do pipeline
- Alertas e notificações
- Resumo de comissões pendentes e repasses

**Rotas:**

| Rota | View | Descrição |
|---|---|---|
| `/dashboard/` | `DashboardView` | Dashboard principal |

---

### 4.19 Relatórios (`reports`)

**Descrição:** Relatórios diversos sobre a operação da corretora.

**Relatórios disponíveis:**

| Relatório | Descrição |
|---|---|
| Carteira de Apólices | Listagem de apólices com filtros por vigência, ramo, seguradora, produtor |
| Comissões Recebidas | Comissões recebidas por período, produtor, agente, seguradora, ramo |
| Comissões Pendentes | Comissões aguardando recebimento |
| Repasses por Agente | Extrato de repasses por agente com totais e status |
| Repasses por Produtor | Extrato de repasses por produtor com totais e status |
| Demonstrativo de Comissão | Visão consolidada: recebido vs repassado vs retido por período |
| Produção por Produtor | Volume de negócios e apólices por produtor |
| Produção por Agente | Volume de negócios e apólices por agente |
| Renovações | Status de renovações, taxa de renovação por período |
| Sinistros | Sinistros por período, status, ramo, seguradora |
| Clientes | Relatório de carteira de clientes, ativos/inativos |
| Pipeline de Vendas | Funil de vendas por período, produtor |
| Seguradoras | Volume por seguradora, ranking |
| Ramos de Seguro | Volume e prêmio por ramo |

**Funcionalidades:**

- Filtros dinâmicos por data, produtor, agente, seguradora, ramo, status
- Exportação em PDF e CSV
- Gráficos complementares

**Rotas:**

| Rota | View | Descrição |
|---|---|---|
| `/reports/` | `ReportIndexView` | Índice de relatórios |
| `/reports/policies/` | `PolicyReportView` | Relatório de apólices |
| `/reports/commissions/` | `CommissionReportView` | Relatório de comissões recebidas |
| `/reports/commissions-pending/` | `CommissionPendingReportView` | Comissões pendentes |
| `/reports/agent-splits/` | `AgentSplitReportView` | Repasses por agente |
| `/reports/producer-splits/` | `ProducerSplitReportView` | Repasses por produtor |
| `/reports/commission-summary/` | `CommissionSummaryReportView` | Demonstrativo consolidado |
| `/reports/production-producer/` | `ProductionProducerReportView` | Produção por produtor |
| `/reports/production-agent/` | `ProductionAgentReportView` | Produção por agente |
| `/reports/renewals/` | `RenewalReportView` | Relatório de renovações |
| `/reports/claims/` | `ClaimReportView` | Relatório de sinistros |
| `/reports/clients/` | `ClientReportView` | Relatório de clientes |
| `/reports/pipeline/` | `PipelineReportView` | Relatório de pipeline |
| `/reports/insurers/` | `InsurerReportView` | Relatório de seguradoras |
| `/reports/branches/` | `BranchReportView` | Relatório por ramo |

---

## 5. Agente de Inteligência Artificial (`ai_agent`)

### 5.1 Visão Geral

O agente de IA é um componente central do SCSI que utiliza **LangChain** e **LangGraph** para fornecer insights, resumos e interações conversacionais sobre os dados da corretora.

### 5.2 Configuração

- **LLM:** Modelo servido pela API da OpenAI (ex: `gpt-5.4`)
- **API Key:** Armazenada em `.env` como `OPENAI_API_KEY`
- **Import:** Variável importada no `settings.py` e usada pela app `ai_agent`
- **Framework:** LangChain para chains e tools, LangGraph para orquestração do agente

### 5.3 Controle de Acesso por Papel

| Papel | Escopo de Dados do Agente |
|---|---|
| `admin` | Todos os dados de todas as corretoras |
| `owner` | Todos os dados da corretora do owner logado |
| `manager` | Todos os dados da corretora do manager logado |
| `agent` | Dados dos seus produtores, negócios e comissões |
| `producer` | Apenas dados vinculados ao produtor logado |

O contexto do agente é construído dinamicamente com base no `request.user` e seu papel, filtrando as queries de acesso a dados.

### 5.4 Models

#### `AISummary`

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `brokerage` | FK(Brokerage) | Sim | Corretora (tenant) |
| `user` | FK(User) | Sim | Usuário que solicitou |
| `content_type` | FK(ContentType) | Sim | Tipo do registro (Client, Deal, Policy, Proposal, Claim) |
| `object_id` | PositiveIntegerField | Sim | ID do registro |
| `content_object` | GenericForeignKey | — | Referência genérica ao registro |
| `summary_text` | TextField | Sim | Texto do resumo gerado |
| `created_at` | DateTimeField | Auto | Data de criação |
| `updated_at` | DateTimeField | Auto | Data de atualização |

#### `AIInsight`

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `brokerage` | FK(Brokerage) | Sim | Corretora (tenant) |
| `user` | FK(User) | Não | Usuário (null = geral da corretora) |
| `insight_type` | CharField | Sim | `dashboard`, `renewal`, `cross_sell`, `commission`, `general` |
| `insight_text` | TextField | Sim | Texto do insight |
| `is_current` | BooleanField | Sim | Se é o insight mais recente |
| `created_at` | DateTimeField | Auto | Data de criação |
| `updated_at` | DateTimeField | Auto | Data de atualização |

#### `ChatSession`

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `brokerage` | FK(Brokerage) | Sim | Corretora (tenant) |
| `user` | FK(User) | Sim | Usuário dono do chat |
| `title` | CharField | Não | Título da sessão (auto-gerado) |
| `is_active` | BooleanField | Sim | Se é a sessão ativa |
| `created_at` | DateTimeField | Auto | Data de criação |
| `updated_at` | DateTimeField | Auto | Data de atualização |

#### `ChatMessage`

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `session` | FK(ChatSession) | Sim | Sessão do chat |
| `role` | CharField (choices) | Sim | `user`, `assistant` |
| `content` | TextField | Sim | Conteúdo da mensagem |
| `created_at` | DateTimeField | Auto | Data de criação |
| `updated_at` | DateTimeField | Auto | Data de atualização |

### 5.5 Funcionalidades do Agente

#### 5.5.1 Insight no Dashboard (Acordeão)

- Componente acordeão no topo do dashboard
- Exibe o insight mais recente gerado pelo agente
- Insight aborda: visão geral de negócios, renovações próximas, sinistros abertos, oportunidades, comissões pendentes
- Gerado via **Django management command**: `python manage.py generate_insights`
- O command itera sobre corretoras ativas e gera insights para cada uma
- Pode ser agendado via cron ou chamado manualmente

**Command:**

```
python manage.py generate_insights
```

- Para cada corretora ativa, coleta dados agregados (deals, renewals, claims, policies, commissions)
- Envia prompt contextual ao LLM via LangChain
- Salva o resultado em `AIInsight` com `is_current=True` (marca anteriores como `False`)

#### 5.5.2 Chat com o Agente

- Tela dedicada acessível pelo menu lateral
- Interface de chat em tempo real
- O agente tem acesso a tools/functions para consultar dados:
  - `search_clients` — buscar clientes
  - `search_policies` — buscar apólices
  - `search_insured_items` — buscar itens segurados
  - `search_deals` — buscar negócios
  - `search_claims` — buscar sinistros
  - `search_renewals` — buscar renovações
  - `get_portfolio_summary` — resumo da carteira
  - `get_renewal_alerts` — alertas de renovação
  - `get_cross_sell_opportunities` — oportunidades de cross/up selling
  - `get_commission_summary` — resumo de comissões
  - `get_pending_splits` — repasses pendentes
  - `get_agent_performance` — desempenho de agentes
  - `get_producer_performance` — desempenho de produtores
- Histórico de conversas armazenado (`ChatSession` + `ChatMessage`)
- Botão para iniciar nova sessão de chat
- Memória da conversa usando histórico de mensagens da sessão atual

**Rotas:**

| Rota | View | Descrição |
|---|---|---|
| `/ai/chat/` | `AIChatView` | Tela do chat |
| `/ai/chat/<session_pk>/` | `AIChatSessionView` | Chat de sessão específica |
| `/ai/chat/new/` | `AIChatNewView` | Criar nova sessão |
| `/ai/chat/send/` | `AIChatSendView` (API) | Enviar mensagem (AJAX/fetch) |

#### 5.5.3 Resumo por IA (Botão "Resumir com IA")

Disponível nas telas de detalhe de:

- **Clientes** (`clients`)
- **Negócios** (`deals`)
- **Apólices** (`policies`)
- **Propostas** (`proposals`)
- **Sinistros** (`claims`)

**Comportamento:**

1. Usuário clica no botão "Resumir com IA" na tela de detalhe do registro
2. Uma requisição AJAX/fetch é enviada para `/ai/summary/`
3. Um loading não-bloqueante aparece na interface (não trava o uso da aplicação)
4. O backend coleta os dados do registro + dados relacionados (incluindo itens segurados, coberturas, comissões)
5. Envia prompt contextual ao LLM via LangChain
6. O resumo retornado é salvo em `AISummary` vinculado ao registro (via `GenericForeignKey`)
7. A resposta é retornada ao frontend e exibida na interface
8. Ao abrir o registro novamente, o último resumo gerado é exibido automaticamente

**Rota API:**

| Rota | View | Descrição |
|---|---|---|
| `/ai/summary/` | `AISummaryView` (API) | Gerar resumo de um registro |

**Payload da requisição:**

```json
{
    "content_type": "clients.client",
    "object_id": 42
}
```

**Resposta:**

```json
{
    "success": true,
    "summary": "Texto do resumo gerado pela IA..."
}
```

### 5.6 Estrutura da App `ai_agent`

```
ai_agent/
├── __init__.py
├── admin.py
├── apps.py
├── models.py              # AISummary, AIInsight, ChatSession, ChatMessage
├── views.py               # Views do chat e API de resumo
├── urls.py
├── forms.py
├── agent.py               # Definição do agente LangGraph
├── tools.py               # Tools/functions do agente (acesso a dados)
├── prompts.py             # Templates de prompts
├── chains.py              # Chains LangChain (resumo, insight)
├── memory.py              # Configuração de memória do agente
├── signals.py             # Signals (se necessário)
├── management/
│   └── commands/
│       └── generate_insights.py   # Command para gerar insights
├── templates/
│   └── ai_agent/
│       ├── chat.html
│       └── components/
│           ├── insight_accordion.html
│           └── summary_button.html
└── templatetags/
    └── ai_tags.py          # Template tags para incluir componentes de IA
```

---

## 6. Multi-Tenancy — Implementação

### 6.1 Mixin de Tenant

```python
# shared/mixins.py

class TenantMixin:
    '''
    Mixin para filtrar querysets pelo brokerage do usuário logado.
    Usar em todas as CBVs que listam ou detalham registros.
    '''
    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role == 'admin':
            return qs
        brokerage = self.request.user.get_active_brokerage()
        return qs.filter(brokerage=brokerage)
```

### 6.2 Mixin de Escopo por Papel

```python
# shared/mixins.py

class RoleScopedMixin:
    '''
    Mixin para filtrar dados conforme o papel do usuário.
    Combinar com TenantMixin.
    '''
    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if user.role in ('admin', 'owner', 'manager'):
            return qs

        if user.role == 'agent':
            agent = user.agent
            producer_ids = agent.producers.values_list('id', flat=True)
            return qs.filter(
                models.Q(agent=agent) |
                models.Q(producer__in=producer_ids)
            )

        if user.role == 'producer':
            return qs.filter(producer=user.producer)

        return qs.none()
```

### 6.3 Middleware de Tenant

```python
# shared/middleware.py

class TenantMiddleware:
    '''
    Injeta o brokerage ativo no request para uso global.
    '''
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            request.current_brokerage = request.user.get_active_brokerage()
        return self.get_response(request)
```

### 6.4 Regras

- Todo model com dados de corretora deve ter FK `brokerage`
- Toda view deve usar `TenantMixin` ou filtrar por `request.current_brokerage`
- Views com dados por papel devem usar `RoleScopedMixin` adicionalmente
- Formulários de criação devem setar automaticamente `brokerage` do usuário logado
- Queries do agente de IA devem respeitar o tenant e o papel

---

## 7. Design System

O design system do SCSI é definido e mantido no arquivo `design_system/design-system.html` na raiz do projeto.

**Regras:**

- Todo componente visual do sistema deve seguir rigorosamente o design system
- Não criar componentes, cores, tipografias ou estilos fora do que está definido
- Qualquer alteração visual deve ser aprovada e refletida no arquivo de design system
- Templates devem referenciar classes e variáveis CSS definidas no design system

---

## 8. Configuração de Ambiente

### 8.1 Arquivo `.env`

```env
SECRET_KEY=sua-secret-key-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
OPENAI_API_KEY=sk-sua-api-key-aqui
OPENAI_MODEL=gpt-5.4
```

### 8.2 `settings.py` — Configurações Relevantes

```python
import os
from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

# OpenAI
OPENAI_API_KEY = config('OPENAI_API_KEY')
OPENAI_MODEL = config('OPENAI_MODEL', default='gpt-5.4')

# Auth
AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# Apps
INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Local
    'shared',
    'accounts',
    'brokerages',
    'agents',
    'plans',
    'clients',
    'insurers',
    'branches',
    'coverages',
    'insured_items',
    'proposals',
    'policies',
    'claims',
    'endorsements',
    'renewals',
    'deals',
    'commissions',
    'reports',
    'dashboard',
    'ai_agent',
    'landing',
]

MIDDLEWARE = [
    # ...padrão Django...
    'shared.middleware.TenantMiddleware',
]
```

### 8.3 `requirements.txt`

```
Django>=6.0,<7.0
python-decouple
Pillow
langchain
langchain-openai
langgraph
```

---

## 9. Estrutura de URLs Principal

```python
# scsi/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('landing.urls')),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('clients/', include('clients.urls')),
    path('insurers/', include('insurers.urls')),
    path('branches/', include('branches.urls')),
    path('coverages/', include('coverages.urls')),
    path('agents/', include('agents.urls')),
    path('producers/', include('agents.urls_producers')),
    path('proposals/', include('proposals.urls')),
    path('policies/', include('policies.urls')),
    path('insured-items/', include('insured_items.urls')),
    path('claims/', include('claims.urls')),
    path('endorsements/', include('endorsements.urls')),
    path('renewals/', include('renewals.urls')),
    path('deals/', include('deals.urls')),
    path('commissions/', include('commissions.urls')),
    path('reports/', include('reports.urls')),
    path('ai/', include('ai_agent.urls')),
]
```

---

## 10. Menu Lateral do Sistema

Estrutura do menu lateral (sidebar) para usuários autenticados:

```
📊 Dashboard
👥 Clientes
🏢 Seguradoras
🏷️ Ramos de Seguro
👔 Agentes
👤 Produtores
📋 Propostas
📄 Apólices
📦 Itens Segurados
⚠️ Sinistros
📝 Endossos
🔄 Renovações
🛡️ Coberturas
💼 Negociações (CRM)
💰 Comissões
   └── Regras de Comissão
   └── Comissões
   └── Repasses
📈 Relatórios
🤖 Agente IA (Chat)
───────────
⚙️ Configurações
   └── Usuários
   └── Grupos e Permissões
👤 Meu Perfil
🚪 Sair
```

**Visibilidade por papel:**

| Item de Menu | Admin | Owner/Manager | Agent | Producer |
|---|---|---|---|---|
| Dashboard | ✅ | ✅ | ✅ | ✅ |
| Clientes | ✅ | ✅ | ✅ | ✅ |
| Seguradoras | ✅ | ✅ | 👁️ | 👁️ |
| Ramos de Seguro | ✅ | ✅ | 👁️ | 👁️ |
| Agentes | ✅ | ✅ | ❌ | ❌ |
| Produtores | ✅ | ✅ | ✅ (seus) | ❌ |
| Propostas | ✅ | ✅ | ✅ | ✅ |
| Apólices | ✅ | ✅ | ✅ | ✅ |
| Sinistros | ✅ | ✅ | ✅ | ✅ |
| Endossos | ✅ | ✅ | ✅ | ✅ |
| Renovações | ✅ | ✅ | ✅ | ✅ |
| Coberturas | ✅ | ✅ | 👁️ | 👁️ |
| Negociações | ✅ | ✅ | ✅ | ✅ |
| Comissões | ✅ | ✅ | ✅ (suas) | ✅ (suas) |
| Relatórios | ✅ | ✅ | 📊 | 📊 |
| Configurações | ✅ | ✅ | ❌ | ❌ |
| Agente IA | ✅ | ✅ | ✅ | ✅ |

---

## 11. Fluxo de Onboarding (Registro)

```
Landing Page
    │
    ▼
Tela de Registro
    │
    ├── Dados do Usuário
    │   ├── Nome completo
    │   ├── Email (será o login)
    │   └── Senha
    │
    ├── Dados da Corretora
    │   ├── CNPJ (obrigatório)
    │   ├── Razão Social (obrigatório)
    │   ├── Nome Fantasia (opcional)
    │   ├── Telefone (opcional)
    │   └── Endereço (opcional)
    │
    └── Escolha do Plano
        ├── Free (sem cartão, acesso imediato)
        ├── Básico (R$ X/usuário/mês)
        ├── Profissional (R$ Y/usuário/mês)
        └── Enterprise (R$ Z/usuário/mês)
            │
            ▼
    Conta criada → Redirect para /dashboard/
```

**Ao criar conta:**

1. Cria o `User` com role `owner`
2. Cria o `Brokerage` com os dados informados e status `active`
3. Cria o `UserBrokerage` vinculando o usuário à corretora
4. Cria a `Subscription` com o plano escolhido
5. Se plano free, status `active` imediatamente
6. Se plano pago, status `pending_payment` até confirmação
7. Cria os `DealStage` padrão para a corretora
8. Cria os `InsuranceBranch` padrão (fixture) para a corretora
9. Redireciona para o dashboard

---

## 12. Permissões e Papéis

### 12.1 Matriz de Permissões por Papel

| Funcionalidade | Admin | Owner | Manager | Agent | Producer |
|---|---|---|---|---|---|
| Ver todas as corretoras | ✅ | ❌ | ❌ | ❌ | ❌ |
| Gerenciar planos | ✅ | ❌ | ❌ | ❌ | ❌ |
| CRUD Clientes | ✅ | ✅ | ✅ | ✅ (seus produtores) | ✅ (apenas seus) |
| CRUD Seguradoras | ✅ | ✅ | ✅ | 👁️ | 👁️ |
| CRUD Ramos de Seguro | ✅ | ✅ | ✅ | 👁️ | 👁️ |
| CRUD Agentes | ✅ | ✅ | ✅ | ❌ | ❌ |
| CRUD Produtores | ✅ | ✅ | ✅ | ✅ (seus) | ❌ |
| CRUD Propostas | ✅ | ✅ | ✅ | ✅ (seus produtores) | ✅ (apenas seus) |
| CRUD Apólices | ✅ | ✅ | ✅ | ✅ (seus produtores) | ✅ (apenas seus) |
| CRUD Itens Segurados | ✅ | ✅ | ✅ | ✅ (seus produtores) | ✅ (apenas seus) |
| CRUD Sinistros | ✅ | ✅ | ✅ | ✅ (seus produtores) | ✅ (apenas seus) |
| CRUD Negociações | ✅ | ✅ | ✅ | ✅ (seus produtores) | ✅ (apenas seus) |
| CRUD Endossos | ✅ | ✅ | ✅ | ✅ (seus produtores) | ✅ (apenas seus) |
| Regras de Comissão | ✅ | ✅ | ✅ | ❌ | ❌ |
| Ver Comissões | ✅ | ✅ | ✅ | ✅ (suas) | ✅ (suas) |
| Pagar Repasses | ✅ | ✅ | ✅ | ❌ | ❌ |
| Relatórios Completos | ✅ | ✅ | ✅ | 📊 (limitado) | 📊 (limitado) |
| Dashboard | ✅ (global) | ✅ (corretora) | ✅ (corretora) | ✅ (seus dados) | ✅ (pessoal) |
| Gestão Usuários | ✅ | ✅ | ✅ | ❌ | ❌ |
| Gestão Grupos/Permissões | ✅ | ✅ | ✅ | ❌ | ❌ |
| Chat IA | ✅ | ✅ | ✅ | ✅ | ✅ |
| Resumo IA | ✅ | ✅ | ✅ | ✅ | ✅ |
| Coberturas | ✅ | ✅ | ✅ | 👁️ | 👁️ |

### 12.2 Implementação

- Usar `PermissionRequiredMixin` nas CBVs
- Criar permissões customizadas nos models quando necessário
- Usar `Group` nativo do Django para agrupar permissões
- Filtros de queryset por papel (`TenantMixin` + `RoleScopedMixin`)

---

## 13. Diagrama de Entidade-Relacionamento (Simplificado)

```
Brokerage (tenant)
├── User (M2M via UserBrokerage)
├── Agent ──┐
│           └── Producer (0..N por Agent)
├── Producer (direto, sem Agent)
├── Client
├── Insurer
├── InsuranceBranch
├── CoverageType ── FK(InsuranceBranch)
├── DealStage
├── CommissionRule ── FK(InsuranceBranch, Insurer, Agent, Producer)
│
├── Proposal ── FK(Client, Insurer, InsuranceBranch, Producer, Agent?)
│   └── InsuredItem (1..N)
│
├── Policy ── FK(Client, Insurer, InsuranceBranch, Producer, Agent?, Proposal?)
│   ├── InsuredItem (1..N)
│   ├── CoverageItem (0..N) ── FK(CoverageType, InsuredItem?)
│   ├── Endorsement (0..N)
│   ├── Renewal (0..N)
│   └── Commission (0..1)
│       └── CommissionSplit (1..N) ── FK(Agent?, Producer?)
│
├── Claim ── FK(Policy, InsuredItem, Client, Insurer)
│
├── Deal ── FK(Client, Producer, Agent?, DealStage, InsuranceBranch?, Insurer?)
│   └── DealActivity (0..N)
│
└── AI
    ├── AISummary (GenericFK → Client, Deal, Policy, Proposal, Claim)
    ├── AIInsight
    └── ChatSession
        └── ChatMessage (0..N)
```

---

## 14. Cronograma Sugerido (Sprints)

### Sprint 1 — Fundação (Semanas 1-2)

- [x] Setup do projeto Django 6.0
- [x] Configuração do design system
- [x] App `shared`): Mixins (TenantMixin, RoleScopedMixin), Middleware
- [x] App `accounts`: User customizado, login via email, registro
- [x] App `brokerages`: Model e admin
- [x] App `plans`: Models e admin
- [x] Templates base (layout, sidebar, header)
- [x] Landing page básica

### Sprint 2 — Cadastros Core (Semanas 3-4)

- [x] App `agents`: CRUD de agentes e produtores
- [x] App `clients`: CRUD completo
- [x] App `insurers`: CRUD completo
- [x] App `branches`: CRUD de ramos + fixtures padrão
- [x] App `coverages`: CRUD de tipos de cobertura
- [x] Implementar TenantMixin + RoleScopedMixin em todas as views
- [x] Permissões por papel nos cadastros

### Sprint 3 — Seguros e Itens Segurados (Semanas 5-7)

- [ ] App `insured_items`: Model e formulários dinâmicos por tipo
- [ ] App `proposals`: CRUD + status workflow + itens segurados inline
- [ ] App `policies`: CRUD + itens segurados inline + coberturas inline
- [ ] App `claims`: CRUD + vínculo com item segurado
- [ ] App `endorsements`: CRUD
- [ ] Conversão proposta → apólice (com cópia de itens segurados)

### Sprint 4 — CRM, Renovações e Comissões (Semanas 8-10)

- [ ] App `deals`: CRUD + visão grid
- [ ] Visão Kanban com drag-and-drop
- [ ] App `renewals`: CRUD + alertas
- [ ] Atividades de negócios
- [ ] App `commissions`: Regras de comissão, cálculo automático, splits
- [ ] Fluxo de recebimento e repasse de comissão
- [ ] Extratos por agente e produtor

### Sprint 5 — Dashboard e Relatórios (Semanas 11-12)

- [ ] App `dashboard`: KPIs e gráficos (incluindo comissões e hierarquia)
- [ ] App `reports`: Todos os relatórios (incluindo comissões, repasses, produção por agente/produtor)
- [ ] Exportação PDF/CSV

### Sprint 6 — Agente de IA (Semanas 13-15)

- [ ] App `ai_agent`: Setup LangChain/LangGraph
- [ ] Tools de acesso a dados (incluindo itens segurados, comissões, agentes, produtores)
- [ ] Insight no dashboard (command + acordeão)
- [ ] Chat com o agente
- [ ] Resumo por IA (botão + API + armazenamento)
- [ ] Integrar resumo em todas as entidades

### Sprint 7 — Polimento (Semanas 16-17)

- [ ] Landing page completa com planos e copy de vendas
- [ ] Fluxo de onboarding completo (com criação de ramos padrão)
- [ ] Gestão de usuários e grupos
- [ ] Revisão de permissões por papel (owner, manager, agent, producer)
- [ ] Revisão de design system
- [ ] Ajustes finais e bugfixes

---

## 15. Riscos e Considerações

| Risco | Mitigação |
|---|---|
| SQLite não escala para produção SaaS | Migrar para PostgreSQL quando necessário (Django ORM abstrai) |
| Custos de API OpenAI | Usar `gpt-5.4` como padrão, limitar chamadas por plano |
| Segurança multi-tenant | Testes rigorosos de isolamento, middleware de tenant, validações |
| Performance do agente IA | Cache de insights, geração assíncrona, rate limiting |
| Complexidade do CRM kanban | Usar biblioteca JS leve para drag-and-drop (SortableJS) |
| Complexidade das regras de comissão | Prioridade clara nas regras, validações de soma = 100%, logs de cálculo |
| JSONField para detalhes de itens segurados | Validação de schema por `item_type`, formulários dinâmicos no frontend |
| Hierarquia agente/produtor + escopo de dados | RoleScopedMixin reutilizável, testes de escopo por papel |
| Sem Docker | Documentar setup manual detalhado |
| Sem testes automatizados | Testes manuais rigorosos, considerar adicionar futuramente |

---

## 16. Glossário

| Termo | Significado |
|---|---|
| **Apólice** | Documento que formaliza o contrato de seguro |
| **Proposta** | Solicitação de seguro antes da emissão da apólice |
| **Sinistro** | Evento coberto pelo seguro que gera indenização |
| **Endosso** | Alteração em uma apólice vigente |
| **Prêmio** | Valor pago pelo segurado à seguradora |
| **IS (Importância Segurada)** | Valor máximo de cobertura |
| **Franquia** | Valor que fica a cargo do segurado em caso de sinistro |
| **SUSEP** | Superintendência de Seguros Privados |
| **Ramo** | Categoria/tipo de seguro (auto, vida, residencial, etc.) |
| **Item Segurado** | Bem, objeto ou sujeito coberto por uma apólice (veículo, imóvel, vida, etc.) |
| **Agente** | Pessoa ou empresa parceira que intermedia vendas para a corretora |
| **Produtor** | Corretor final que realiza a venda, vinculado a um agente ou à corretora |
| **Corretora** | Empresa de corretagem de seguros |
| **Comissão** | Valor pago pela seguradora à corretora pela venda do seguro |
| **Repasse (Split)** | Parcela da comissão repassada ao agente ou produtor |
| **Cross-selling** | Venda de produtos complementares ao cliente |
| **Up-selling** | Venda de cobertura/plano superior ao cliente |
| **Tenant** | Unidade isolada de dados (cada corretora é um tenant) |
| **SaaS** | Software como Serviço |

---

## 17. Referências

- Django 6.0 Documentation: https://docs.djangoproject.com/
- LangChain Documentation: https://python.langchain.com/
- LangGraph Documentation: https://langchain-ai.github.io/langgraph/
- OpenAI API Reference: https://platform.openai.com/docs/
- PEP 08: https://peps.python.org/pep-0008/
- Design System: `design_system/design-system.html` (interno ao projeto)
- Ambiente Virtual do projeto: .venv
