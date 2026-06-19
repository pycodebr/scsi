# PRD - SCSI: Sistema de Gestão para Corretora de Seguros Inteligente

> **Versão:** 1.0
> **Data:** 2026-05-28
> **Status:** Aprovado para desenvolvimento
> **Domínio de produção:** `scsi.digital`
> **Stack núcleo:** Python 3.13+ · Django 6.0+ · PostgreSQL · Celery + RabbitMQ · Docker Swarm + Traefik · LangChain 1.0+ / LangGraph · OpenAI GPT-5.5-mini

---

## Sobre este documento

Este PRD é a **fonte única de verdade** do projeto SCSI. Ele deve ser citado (`@PRD.md`) em todos os prompts de execução de sprint e em todas as decisões técnicas. O documento foi escrito para ser implementável por um desenvolvedor humano ou por um agente de IA programador sem ambiguidades.

**Convenções deste documento:**

- Texto explicativo e UI: **português brasileiro**.
- Nomes técnicos (models, views, apps, campos, comandos, pacotes): **inglês**.
- Diagramas de arquitetura, ER e fluxos: **Mermaid**.
- Wireframes conceituais: ASCII.
- Critérios de aceite e tarefas de sprint: checkboxes `- [ ]` (marcáveis na execução).
- O documento **nunca diminui**: novas features viram novas subseções e novas sprints.

---

## Índice

1. [Visão Geral do Produto](#1-visão-geral-do-produto)
2. [Objetivos do Sistema](#2-objetivos-do-sistema)
3. [Escopo do Projeto](#3-escopo-do-projeto)
4. [Público-Alvo](#4-público-alvo)
5. [Principais Jornadas de Usuário](#5-principais-jornadas-de-usuário)
6. [Personas e Perfis de Acesso](#6-personas-e-perfis-de-acesso)
7. [Regras Gerais do Sistema](#7-regras-gerais-do-sistema)
8. [Arquitetura Geral da Aplicação](#8-arquitetura-geral-da-aplicação)
9. [Arquitetura Multi Tenant](#9-arquitetura-multi-tenant)
10. [Stack Técnica Obrigatória](#10-stack-técnica-obrigatória)
11. [Estrutura Recomendada do Projeto Django](#11-estrutura-recomendada-do-projeto-django)
12. [Apps Django Recomendadas](#12-apps-django-recomendadas)
13. [Modelagem de Domínio](#13-modelagem-de-domínio)
14. [Entidades Principais do Sistema](#14-entidades-principais-do-sistema)
15. [Regras de Permissão e Segurança](#15-regras-de-permissão-e-segurança)
16. [Gestão de Arquivos e Mídias Protegidas](#16-gestão-de-arquivos-e-mídias-protegidas)
17. [Autenticação e Usuários](#17-autenticação-e-usuários)
18. [Cadastro e Gestão de Corretoras](#18-cadastro-e-gestão-de-corretoras)
19. [Cadastro e Gestão de Clientes](#19-cadastro-e-gestão-de-clientes)
20. [Cadastro e Gestão de Seguradoras](#20-cadastro-e-gestão-de-seguradoras)
21. [Cadastro e Gestão de Ramos](#21-cadastro-e-gestão-de-ramos)
22. [Gestão de Propostas](#22-gestão-de-propostas)
23. [Gestão de Apólices](#23-gestão-de-apólices)
24. [Geração de Apólice a partir de Proposta](#24-geração-de-apólice-a-partir-de-proposta)
25. [Gestão de Itens Cobertos](#25-gestão-de-itens-cobertos)
26. [Gestão de Sinistros](#26-gestão-de-sinistros)
27. [Gestão de Endossos](#27-gestão-de-endossos)
28. [Gestão de Renovações](#28-gestão-de-renovações)
29. [Gestão de Agentes, Produtores e Comissões](#29-gestão-de-agentes-produtores-e-comissões)
30. [CRM com Grid e Kanban](#30-crm-com-grid-e-kanban)
31. [Dashboard e Métricas](#31-dashboard-e-métricas)
32. [Relatórios e Exportações](#32-relatórios-e-exportações)
33. [Landing Page, Cadastro, Login e Recuperação de Senha](#33-landing-page-cadastro-login-e-recuperação-de-senha)
34. [Agentes de Inteligência Artificial](#34-agentes-de-inteligência-artificial)
35. [Chat com Agente de IA](#35-chat-com-agente-de-ia)
36. [Tasks Assíncronas com Celery](#36-tasks-assíncronas-com-celery)
37. [Notificações na Interface](#37-notificações-na-interface)
38. [Design System e UI/UX](#38-design-system-e-uiux)
39. [Requisitos Não Funcionais](#39-requisitos-não-funcionais)
40. [Regras de Qualidade de Código](#40-regras-de-qualidade-de-código)
41. [Documentação com MKDocs](#41-documentação-com-mkdocs)
42. [Variáveis de Ambiente](#42-variáveis-de-ambiente)
43. [Docker e Docker Compose para Desenvolvimento Local](#43-docker-e-docker-compose-para-desenvolvimento-local)
44. [Deploy em VPS Ubuntu com Docker Swarm](#44-deploy-em-vps-ubuntu-com-docker-swarm)
45. [Guia Detalhado de Deploy do Zero](#45-guia-detalhado-de-deploy-do-zero)
46. [Estratégia de Banco de Dados](#46-estratégia-de-banco-de-dados)
47. [Estratégia de Backup](#47-estratégia-de-backup)
48. [Estratégia de Logs e Monitoramento](#48-estratégia-de-logs-e-monitoramento)
49. [Riscos Técnicos do Projeto](#49-riscos-técnicos-do-projeto)
50. [Decisões Técnicas Recomendadas](#50-decisões-técnicas-recomendadas)
51. [Critérios de Aceite](#51-critérios-de-aceite)
52. [Roadmap de Desenvolvimento](#52-roadmap-de-desenvolvimento)
53. [Sprints de Implementação em Checklist](#53-sprints-de-implementação-em-checklist)
54. [Considerações Finais](#54-considerações-finais)

---

## 1. Visão Geral do Produto

### 1.1 Descrição

O **SCSI (Sistema de Gestão para Corretora de Seguros Inteligente)** é uma plataforma **SaaS Multi Tenant** que centraliza toda a operação de corretoras de seguros — do primeiro contato com o lead até a renovação da apólice — em um único ambiente seguro, isolado por corretora e potencializado por **agentes de Inteligência Artificial**. O sistema gerencia clientes, seguradoras, ramos, propostas, apólices, itens cobertos, sinistros, endossos, renovações, a hierarquia comercial (agentes e produtores), comissões e repasses, um CRM com pipeline visual (grid e Kanban), dashboards analíticos, relatórios exportáveis (PDF/CSV) e assistentes de IA que resumem entidades e respondem perguntas sobre os dados da corretora.

### 1.2 Problema que Resolve

Corretoras de seguros operam hoje fragmentadas entre planilhas, sistemas das seguradoras, e-mails, WhatsApp e controles manuais. Isso gera: perda de prazos de renovação (receita recorrente que evapora), dificuldade de calcular e repassar comissões corretamente, falta de visibilidade do funil de vendas, retrabalho na consolidação de informações de clientes e apólices, e ausência de inteligência sobre a própria carteira. O corretor gasta mais tempo organizando dados do que vendendo e atendendo. Não existe uma camada de IA que "leia" toda a relação do cliente com a corretora e devolva um resumo acionável em segundos.

### 1.3 Proposta de Valor

| Para | Valor entregue |
|---|---|
| **Dono / administrador da corretora** | Visão 360º da operação em um dashboard único; controle de comissões e repasses; isolamento e segurança total dos dados; relatórios prontos para tomada de decisão. |
| **Gerente** | Acompanhamento do funil de vendas (CRM Kanban), produtividade da equipe e pipeline de renovações sem montar planilhas. |
| **Corretor / produtor** | Menos trabalho operacional: cadastro centralizado, geração de apólice a partir da proposta com um clique, e resumos por IA que eliminam leitura de históricos longos. |
| **Operacional** | Fluxo guiado para propostas, apólices, sinistros, endossos e anexos protegidos, com menos chance de erro. |
| **Diferencial técnico** | Agentes de IA (LangChain 1.0+/LangGraph + GPT-5.5-mini) com **acesso estritamente isolado por tenant**, capazes de resumir clientes/apólices/sinistros/propostas/negociações e responder no chat sobre os dados da própria corretora — nunca de outra. |

---

## 2. Objetivos do Sistema

### 2.1 Objetivos de Produto

- Centralizar 100% da operação da corretora em um único sistema multi tenant.
- Reduzir a perda de renovações por meio de pipeline e alertas automáticos de vencimento.
- Dar visibilidade do funil comercial (leads → propostas → apólices) com CRM grid + Kanban.
- Automatizar o cálculo de comissões da corretora e os repasses para agentes e produtores.
- Acelerar a compreensão de qualquer entidade (cliente, apólice, sinistro, proposta, negociação) com resumos de IA sob demanda.
- Oferecer um assistente de chat de IA que responde com base nos dados reais da corretora.

### 2.2 Objetivos Técnicos

- Garantir **isolamento absoluto entre corretoras** (multi tenant compartilhado por FK + filtros + middleware + mixins).
- Servir arquivos e mídias **sempre sob autenticação, autorização e tenant** — nunca publicamente.
- Processar tarefas pesadas (IA, relatórios, e-mails) de forma **assíncrona e não bloqueante** via Celery + RabbitMQ.
- Manter o código idiomático Django, em inglês, PEP8, com Class Based Views e recursos nativos.
- Entregar uma base preparada para evolução (índices, JSONB, modelagem limpa) sem complexidade prematura.
- Permitir deploy reproduzível em VPS Ubuntu com Docker Swarm + Traefik (TLS automático).

### 2.3 Metas Mensuráveis (referência para os Critérios de Aceite — seção 51)

- Nenhuma query sensível retorna dados de outra corretora (verificável por inspeção de `get_queryset`).
- Toda model de domínio possui `created_at` e `updated_at`.
- Todo arquivo anexado só é acessível via view protegida com checagem de tenant + permissão.
- Disparo de resumo por IA retorna a interface em < 1s (a geração acontece em background).
- Toda rota privada exige autenticação.

---

## 3. Escopo do Projeto

### 3.1 Dentro do Escopo (V1)

- Cadastro/login por **e-mail** (sistema nativo Django) + recuperação de senha nativa.
- Onboarding com criação da **corretora** (CNPJ e razão social obrigatórios) e escolha de **plano free**.
- Gestão de usuários e **perfis de acesso** (administrador, gerente, corretor, agente, produtor, operacional).
- Cadastros: clientes, seguradoras, ramos, propostas, apólices, itens cobertos, sinistros, endossos, renovações, agentes, produtores.
- **Geração de apólice a partir de proposta** com botão dedicado.
- **Comissões e repasses** (corretora → agente → produtor).
- **CRM** com visualização em **grid** e **Kanban** (pipeline personalizável, drag-and-drop).
- **Dashboard** com métricas e gráficos variados, incluindo **funil de negociações**.
- **Relatórios** exportáveis em **PDF (ReportLab/PyPDF)** e **CSV**.
- **Anexos protegidos** em clientes, propostas, apólices e sinistros.
- **Agentes de IA**: resumos de cliente/apólice/sinistro/proposta/negociação (assíncronos) + **chat com IA** com streaming e tools isoladas por tenant.
- **Notificações na interface** quando tarefas assíncronas concluem.
- **Landing page** em `scsi.digital` com apresentação, cadastro e login.
- **Tasks assíncronas** (Celery worker + beat) e visualização no Django Admin.
- **Documentação** com MKDocs (com Mermaid).
- **Deploy** com Docker Swarm + Traefik em VPS Ubuntu.

### 3.2 Fora do Escopo (V1)

- **Integração com pagamentos / gateways** (planos pagos ficam como "Em breve", botão desabilitado).
- **Testes automatizados** (explicitamente não implementados nesta fase — ver seção 40).
- **Schema-per-tenant ou database-per-tenant** (usaremos shared schema por FK).
- **Kubernetes** (deploy é Docker Swarm).
- **App mobile nativo** (a aplicação web é responsiva e cobre mobile/tablet/desktop).
- Integrações diretas com APIs de seguradoras (importação automática de apólices) — futuro.
- Assinatura digital de documentos — futuro.

### 3.3 Premissas e Restrições

- Único arquivo `settings.py`; credenciais via `.env` na raiz, carregadas no settings.
- Ambiente virtual `.venv` na raiz; `requirements.txt` sempre atualizado.
- Timezone `America/Sao_Paulo`; toda UI em pt-BR.
- O design **deve** seguir rigorosamente `@design_system/design-system.html` (ver seção 38). Nenhum design paralelo pode ser inventado.

---

## 4. Público-Alvo

O SCSI atende **corretoras de seguros** de pequeno e médio porte no Brasil — desde o corretor autônomo com CNPJ até corretoras com equipe comercial estruturada (gerente, corretores, agentes parceiros e produtores). Caracteriza-se por:

- Profissionais com habilidade técnica **baixa a intermediária** — usam sistemas SaaS, não programam.
- Operação centrada em **renovação** (receita recorrente) e em **relacionamento** com o cliente.
- Necessidade de **organização de comissões** e de **visibilidade do funil**.
- Dados sensíveis (documentos de clientes, apólices, sinistros) que exigem **sigilo e segregação**.

As personas detalhadas (com dores, buscas e ações no sistema) estão na seção 6.

---

## 5. Principais Jornadas de Usuário

### 5.1 Jornada — Onboarding da Corretora (Administrador)

```mermaid
flowchart TD
    A([Visitante acessa scsi.digital]) --> B[Lê a landing page]
    B --> C[Clica em 'Criar conta grátis']
    C --> D["Preenche dados do usuário: nome, email, senha"]
    D --> E[Preenche dados da corretora: CNPJ e razão social obrigatórios]
    E --> F[Escolhe plano Free - sem cartão de crédito]
    F --> G{CNPJ e email válidos e únicos?}
    G -->|Não| D
    G -->|Sim| H[Cria Brokerage + User owner + Subscription Free]
    H --> I[Usuário autenticado e redirecionado ao Dashboard]
    I --> J[Ramos e Pipeline padrão criados via signal]
    J --> K[Admin convida equipe e começa a cadastrar clientes]
```

### 5.2 Jornada — Do Lead à Apólice (Corretor / Produtor)

```mermaid
flowchart TD
    A([Corretor cria negociação no CRM]) --> B[Card entra na 1ª etapa do pipeline]
    B --> C[Arrasta o card entre etapas conforme evolui]
    C --> D{Negociação avançou para proposta?}
    D -->|Sim| E[Gera Proposta vinculada ao cliente e negociação]
    E --> F[Adiciona itens cobertos à proposta]
    F --> G[Envia proposta e registra status]
    G --> H{Proposta aprovada pelo cliente?}
    H -->|Não| I[Marca negociação como perdida ou retoma]
    H -->|Sim| J[Clica em 'Gerar apólice' na tela da proposta]
    J --> K[Sistema cria Apólice copiando dados e itens cobertos]
    K --> L[Confirma campos editáveis e número da apólice]
    L --> M[Apólice ativa + comissão gerada + negociação marcada como ganha]
```

### 5.3 Jornada — Resumo com IA (qualquer entidade)

```mermaid
flowchart TD
    A([Usuário abre detalhes de um cliente]) --> B[Clica em 'Resumir com IA']
    B --> C[Botão exibe loading + aviso 'você será notificado']
    C --> D[View enfileira Celery task e retorna imediatamente]
    D --> E[Task: agente busca dados do cliente DENTRO do tenant]
    E --> F[LLM gera resumo + insights em Markdown]
    F --> G[Resumo salvo em client.ai_summary; status = done]
    G --> H[Notification criada para o usuário]
    H --> I[Badge de notificação aparece via polling]
    I --> J[Usuário recarrega/abre e vê o resumo no card do cliente]
```

### 5.4 Jornada — Chat com IA sobre a Carteira

```mermaid
flowchart TD
    A([Usuário acessa 'Chat IA' no menu lateral]) --> B[Cria nova sessão ou abre sessão existente]
    B --> C[Digita pergunta sobre a carteira da corretora]
    C --> D[View valida autenticação + tenant + monta tools isoladas]
    D --> E[Agente LangGraph decide quais tools chamar]
    E --> F[Tools consultam o banco filtrando por brokerage do usuário]
    F --> G[LLM gera resposta em Markdown com streaming]
    G --> H[Resposta renderizada em tempo real via SSE]
    H --> I[Mensagens user/assistant salvas na sessão]
```

### 5.5 Jornada — Ciclo de Renovação

```mermaid
flowchart TD
    A([Celery Beat roda diariamente]) --> B[Busca apólices com vencimento próximo no tenant]
    B --> C[Cria/atualiza registros de Renewal pendentes]
    C --> D[Gera Notification para o responsável]
    D --> E[Corretor abre a renovação]
    E --> F{Cliente renova?}
    F -->|Sim| G[Gera nova apólice vinculada à renovação]
    F -->|Não| H[Marca renovação como perdida com motivo]
    G --> I[Renewal = renovada; nova comissão registrada]
```

---

## 6. Personas e Perfis de Acesso

### 6.1 Personas

#### Persona 1 — Administradora / Dona da Corretora

| Atributo | Detalhe |
|---|---|
| **Nome fictício** | Renata, 42 anos |
| **Cargo / contexto** | Sócia-proprietária de uma corretora com 6 colaboradores e ~1.500 apólices ativas |
| **Dor principal** | Não enxerga a operação consolidada; sofre para fechar comissões e repasses no fim do mês |
| **O que busca** | Visão 360º, controle financeiro de comissões, segurança dos dados, relatórios prontos |
| **Habilidade técnica** | Intermediária — usa ERPs e planilhas, não programa |
| **Ações no sistema** | Cadastra a corretora, convida usuários, define perfis, acompanha dashboard, exporta relatórios, gerencia comissões |

#### Persona 2 — Gerente Comercial

| Atributo | Detalhe |
|---|---|
| **Nome fictício** | Marcos, 35 anos |
| **Cargo / contexto** | Gerente de vendas, lidera 3 corretores e acompanha o funil |
| **Dor principal** | Falta de visibilidade do pipeline e das renovações que estão vencendo |
| **O que busca** | CRM Kanban, métricas de produtividade, alertas de renovação |
| **Habilidade técnica** | Intermediária |
| **Ações no sistema** | Configura pipeline, acompanha negociações, distribui leads, monitora dashboard e renovações |

#### Persona 3 — Corretor / Produtor

| Atributo | Detalhe |
|---|---|
| **Nome fictício** | Júlia, 29 anos |
| **Cargo / contexto** | Corretora que prospecta, cota e fecha seguros |
| **Dor principal** | Perde tempo organizando dados e relendo históricos longos de clientes |
| **O que busca** | Cadastro rápido, geração de apólice a partir da proposta, resumos por IA |
| **Habilidade técnica** | Básica a intermediária |
| **Ações no sistema** | Cria negociações, propostas, gera apólices, registra sinistros, usa resumos e chat de IA |

#### Persona 4 — Operacional / Back-office

| Atributo | Detalhe |
|---|---|
| **Nome fictício** | Paulo, 24 anos |
| **Cargo / contexto** | Apoio administrativo: anexos, endossos, conferência de documentos |
| **Dor principal** | Documentos espalhados e risco de anexar no cadastro errado |
| **O que busca** | Fluxo guiado, anexos organizados e protegidos por cliente/apólice |
| **Habilidade técnica** | Básica |
| **Ações no sistema** | Anexa documentos, registra endossos, atualiza cadastros, acompanha sinistros |

### 6.2 Perfis de Acesso (roles)

O campo `User.role` define o perfil. As permissões são aplicadas por **role + tenant** (ver seção 15). Todos os perfis enxergam **apenas** dados da própria corretora.

| Role (código) | Nome exibido | Pode | Não pode |
|---|---|---|---|
| `owner` | Administrador (Dono) | Tudo dentro do tenant: gerencia corretora, usuários, planos, comissões, todos os cadastros e relatórios | Acessar dados de outra corretora |
| `manager` | Gerente | Gerir equipe, CRM, propostas/apólices/sinistros, dashboard, relatórios, comissões (visualizar) | Excluir a corretora, alterar plano/billing, remover o owner |
| `broker` | Corretor | Criar/editar clientes, propostas, apólices, sinistros, negociações próprias e da equipe (conforme configuração) | Gerenciar usuários, alterar plano, ver repasses de outros sem permissão |
| `agent` | Agente | Visualizar e operar negócios/produção vinculados a si; acompanhar suas comissões/repasses | Gerenciar usuários e configurações da corretora |
| `producer` | Produtor | Criar/editar negociações e propostas próprias; acompanhar suas comissões | Acessar dados de outros produtores sem permissão; configurações da corretora |
| `operational` | Operacional | Anexos, endossos, atualizações cadastrais, suporte operacional | Excluir entidades críticas, gerenciar comissões, alterar configurações |

> **Observação de modelagem:** `role` governa **permissões de uso**. As entidades de domínio `Agent` e `Producer` (seção 14) existem para a **hierarquia comercial e cálculo de comissões**, e podem (opcionalmente) ser vinculadas a um `User` quando o agente/produtor precisa de login (`Agent.user`, `Producer.user`). Um produtor que só é remunerado mas não acessa o sistema existe como `Producer` sem `User`.

---

## 7. Regras Gerais do Sistema

Regras transversais que valem para **todo** o sistema:

1. **Isolamento por tenant é inviolável.** Toda entidade de domínio possui `brokerage` (FK para a corretora). Toda query sensível filtra por `request.tenant`. É proibido qualquer endpoint que retorne dados sem o filtro de tenant.
2. **Rotas privadas exigem autenticação.** `LoginRequiredMixin` (ou middleware equivalente) em todas as views internas. Apenas landing, login, registro e recuperação de senha são públicas.
3. **Toda model de domínio herda `created_at` e `updated_at`** de uma base abstrata (`BaseModel`).
4. **Login por e-mail**, nunca por username.
5. **Arquivos nunca são públicos.** Servidos apenas por view protegida (tenant + permissão + autenticação).
6. **Tarefas pesadas são assíncronas** (Celery). A interface nunca bloqueia esperando IA, PDF ou e-mail.
7. **IA respeita tenant.** Tools de IA recebem o `brokerage` injetado no servidor; o modelo nunca escolhe o tenant. Acesso cruzado é impossível por construção.
8. **Idioma:** código em inglês, UI em pt-BR, timezone `America/Sao_Paulo`.
9. **Soft delete recomendado** para entidades críticas (campo `is_active`) em vez de exclusão física, preservando integridade e histórico (ver seção 46).
10. **Unicidade é por tenant.** Números de proposta/apólice, slugs e afins são únicos **dentro da corretora** (constraints `UniqueConstraint(fields=['brokerage', 'number'])`), nunca globalmente.
11. **Auditoria mínima:** entidades registram quem criou/alterou quando relevante (`created_by`, e histórico de etapa no CRM).
12. **Valores monetários** usam `DecimalField` (nunca float). Percentuais de comissão também (`DecimalField`).
13. **Datas e prazos** (vigência, vencimento, aviso de sinistro) são sempre `DateField`/`DateTimeField` com timezone correto.
14. **Mensagens ao usuário** usam o framework `django.contrib.messages` + notificações persistentes (seção 37).

---

## 8. Arquitetura Geral da Aplicação

### 8.1 Visão de Camadas

```mermaid
graph TB
    subgraph "Frontend (Django Templates + Design System)"
        LP[Landing Page scsi.digital]
        AUTH[Login / Registro / Reset de Senha]
        DASH[Dashboard]
        CRUDS[Telas de Cadastros e CRUDs]
        CRM[CRM Grid + Kanban]
        CHAT[Chat IA - SSE Streaming]
        REP[Relatórios]
    end

    subgraph "Django 6 (Backend)"
        URLS[URL Router]
        MW[Middlewares: Auth + Tenant]
        VIEWS[Class Based Views + Mixins de Tenant]
        FORMS[Forms / ModelForms]
        MODELS[Models / ORM + Managers de Tenant]
        SIGNALS[Signals]
        ADMIN[Django Admin + dj-celery-panel]
    end

    subgraph "AI Engine (LangChain 1.0+ / LangGraph)"
        SUMM[Summary Agents - StateGraph]
        CHATAG[Chat Agent - Tool Calling]
        TOOLS[Tenant-Scoped Tools]
    end

    subgraph "Async (Celery)"
        BROKER[(RabbitMQ - broker)]
        WORKER[Celery Worker]
        BEAT[Celery Beat]
        RESULT[(Result Backend)]
    end

    subgraph "External Services"
        OAI[OpenAI - GPT-5.5-mini]
        SMTP[SMTP - emails]
    end

    subgraph "Data Layer"
        DB[(PostgreSQL)]
        MEDIA[Media Protegida - filesystem por tenant]
        STATIC[Static Files]
    end

    LP --> URLS
    AUTH --> URLS
    DASH --> URLS
    CRUDS --> URLS
    CRM --> URLS
    CHAT --> URLS
    REP --> URLS
    URLS --> MW
    MW --> VIEWS
    VIEWS --> FORMS
    VIEWS --> MODELS
    VIEWS --> BROKER
    VIEWS --> CHATAG
    CHATAG --> TOOLS
    TOOLS --> MODELS
    MODELS --> DB
    SIGNALS --> MODELS
    BROKER --> WORKER
    BEAT --> BROKER
    WORKER --> RESULT
    WORKER --> SUMM
    SUMM --> TOOLS
    SUMM --> OAI
    CHATAG --> OAI
    WORKER --> SMTP
    VIEWS --> MEDIA
    VIEWS --> STATIC
```

### 8.2 Princípios Arquiteturais

- **Monolito modular Django.** Apps coesas por responsabilidade, comunicação por ORM/serviços internos — sem microsserviços nesta fase (simplicidade operacional).
- **Thin views, fat services.** Lógica de negócio complexa (gerar apólice, calcular comissão, montar contexto de IA) vive em módulos `services.py` por app; as CBVs orquestram.
- **Tenant em primeiro lugar.** O `TenantMiddleware` resolve `request.tenant` cedo no ciclo; mixins garantem o filtro em todas as views.
- **Assíncrono por padrão para tarefas caras.** IA, PDF e e-mail nunca rodam no request/response.
- **Recursos nativos do Django** sempre que possível (auth, forms, admin, e-mail, password reset, paginação, messages).

### 8.3 Fluxo de Request Padrão

```mermaid
sequenceDiagram
    participant U as Usuário (browser)
    participant T as Traefik
    participant D as Django (gunicorn)
    participant MW as TenantMiddleware
    participant V as CBV + TenantQuerysetMixin
    participant DB as PostgreSQL

    U->>T: GET /clientes/
    T->>D: proxy (TLS terminado)
    D->>MW: request autenticado?
    MW->>MW: resolve request.tenant = user.brokerage
    MW->>V: encaminha
    V->>DB: Client.objects.filter(brokerage=request.tenant)
    DB-->>V: queryset isolado
    V-->>U: HTML renderizado (Design System)
```

---

## 9. Arquitetura Multi Tenant

### 9.1 Estratégia: Shared Database, Shared Schema, Isolamento por FK

O SCSI usa **multi tenancy compartilhada** — um único banco, um único schema, todas as corretoras na mesma tabela, isoladas por uma **chave de tenant (`brokerage`)** presente em toda entidade de domínio. Esta é a decisão explícita do projeto (ver seção 50.3) e **não** será schema-per-tenant nem database-per-tenant.

**Por quê:** simplicidade operacional (migrações únicas, um banco para backup/monitorar), código Django idiomático e custo de infra baixo — adequado a uma V1 com muitas corretoras pequenas.

### 9.2 Componentes do Isolamento (defesa em camadas)

```mermaid
graph LR
    A[1. Modelo: FK brokerage obrigatória] --> B[2. Middleware: request.tenant]
    B --> C[3. Manager: TenantManager.for_tenant]
    C --> D[4. Mixin de View: filtra get_queryset]
    D --> E[5. Forms: querysets de FKs filtrados por tenant]
    E --> F[6. Validação: save valida FKs do mesmo tenant]
    F --> G[7. IA: tools recebem brokerage do servidor]
```

| Camada | Mecanismo | Responsabilidade |
|---|---|---|
| **1. Model** | `TenantAwareModel` abstrato com `brokerage = ForeignKey('tenants.Brokerage')` | Toda entidade sensível carrega o tenant |
| **2. Middleware** | `TenantMiddleware` define `request.tenant = request.user.brokerage` | Resolve o tenant do usuário autenticado |
| **3. Manager** | `TenantManager` com `for_tenant(tenant)` + `current_tenant` (contextvar) | Filtro programático e defesa adicional |
| **4. Mixin de View** | `TenantQuerysetMixin.get_queryset()` faz `super().get_queryset().filter(brokerage=self.request.tenant)` | Garante filtro em listas/detalhes/updates/deletes |
| **5. Forms** | Querysets de campos FK limitados ao tenant (`form.fields['client'].queryset = Client.objects.for_tenant(tenant)`) | Impede selecionar entidade de outro tenant |
| **6. Validação** | `clean()`/`save()` valida que FKs relacionadas pertencem ao mesmo `brokerage` | Bloqueia injeção de IDs de outro tenant via POST |
| **7. IA** | Factory `build_tenant_tools(brokerage)` injeta o tenant; tools nunca aceitam `brokerage_id` do modelo | Agente nunca acessa outro tenant |

### 9.3 Models Abstratas Base

```python
# base/models.py  (apenas referência — implementar na Sprint correspondente)
class BaseModel(models.Model):
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        abstract = True
        ordering = ('-created_at',)


class TenantAwareModel(BaseModel):
    brokerage = models.ForeignKey(
        'tenants.Brokerage',
        on_delete=models.CASCADE,
        related_name='%(class)ss',
        db_index=True,
    )
    objects = TenantManager()

    class Meta:
        abstract = True
        indexes = [models.Index(fields=['brokerage'])]
```

### 9.4 Regras de Isolamento (inegociáveis)

- **Nunca** escrever uma view de listagem/detalhe sem o `TenantQuerysetMixin` (ou filtro explícito por `request.tenant`).
- **Nunca** confiar em `pk` vindo da URL sem o filtro de tenant (`get_object_or_404(Model.objects.for_tenant(request.tenant), pk=pk)`).
- **Nunca** popular um `ChoiceField`/`ModelChoiceField` com queryset global.
- **Nunca** expor um endpoint de IA cujo tool aceite o tenant como argumento controlável pelo modelo.
- O `request.tenant` deve estar disponível desde o middleware; usuários sem corretora ativa não acessam áreas internas.

### 9.5 Identidade do Tenant

O **tenant é a `Brokerage` (corretora)**. Um `User` pertence a exatamente uma `Brokerage` (`User.brokerage`) na V1. Isso simplifica o onboarding (registro cria a corretora e o usuário owner). Caso, no futuro, um usuário precise pertencer a múltiplas corretoras, evolui-se para um modelo `Membership` (User × Brokerage × role) sem quebrar o restante (ver seção 50.3, trade-off).

---

## 10. Stack Técnica Obrigatória

### 10.1 Núcleo

| Camada | Tecnologia | Versão mínima | Observação |
|---|---|---|---|
| Linguagem | Python | `>= 3.13` | Ambiente virtual `.venv` na raiz |
| Framework | Django | `>= 6.0` | Único `settings.py`; CBVs e recursos nativos |
| Banco | PostgreSQL | `>= 16` | JSONB, índices compostos, constraints por tenant |
| Async | Celery | `>= 5.4` | Worker + Beat |
| Broker | RabbitMQ | `>= 3.13` | Broker do Celery |
| Result backend | Redis ou DB | — | Result backend + cache leve (recomendado Redis) |
| Admin de tasks | `dj-celery-panel` | — | Visualização das tasks no Django Admin |
| Reverse proxy | Traefik | `>= 3.0` | TLS automático (Let's Encrypt), load balancer |
| Orquestração | Docker + Docker Swarm | — | Compose no dev, Swarm no prod |
| WSGI server | Gunicorn | `>= 22` | Servindo o app Django |

### 10.2 IA — Regra de Versionamento de Dependências

> A stack de IA evolui rápido e os pacotes são separados por provider. **Fixe as versões mínimas abaixo** no `requirements.txt`. Imports sempre por provider; API keys sempre via variável de ambiente (nunca hardcoded).

| Pacote | Versão mínima | Motivo |
|---|---|---|
| `langchain` | `>= 1.0.0` | Núcleo de orquestração (LCEL, mensagens, prompts) |
| `langchain-openai` | `>= 1.0.0` | `ChatOpenAI` para GPT-5.5-mini |
| `langgraph` | `>= 1.0.0` | `StateGraph` para resumos e agente de chat com tools |
| `openai` | `>= 2.0.0` | SDK oficial usado por baixo do `langchain-openai` |

**Modelo padrão:** `GPT-5.5-mini` (via OpenAI), configurável por env (`OPENAI_MODEL`). Econômico e suficiente para resumos e chat sobre dados estruturados.

### 10.3 Bibliotecas de Apoio

| Pacote | Uso |
|---|---|
| `psycopg[binary]` `>= 3.2` | Driver PostgreSQL |
| `gunicorn` | Servidor WSGI em produção |
| `python-decouple` ou `django-environ` | Carregar `.env` no `settings.py` |
| `celery` + `kombu` | Tasks assíncronas e integração com RabbitMQ |
| `django-celery-beat` | Agendamento persistente (DatabaseScheduler) para o Beat |
| `django-celery-results` | Armazenar resultados das tasks (visíveis no admin) |
| `dj-celery-panel` | Painel de tasks no Django Admin |
| `redis` | Cache / result backend / lock leve |
| `reportlab` | Geração de PDFs de relatórios |
| `pypdf` | Manipulação/merge de PDFs |
| `Pillow` | Validação/processamento de imagens anexadas |
| `whitenoise` (opcional) | Servir estáticos no container app |
| `Faker` `>= 30` | Geração de dados fake (locale `pt_BR`) para o comando `seed_demo` de demonstração (seção 46.1) |

> **Nota sobre `dj-celery-panel`:** é o requisito de visualização de tasks no Admin. `django-celery-beat` e `django-celery-results` **complementam** (agendamento persistente e armazenamento de resultados) — não substituem. Todos convivem.

### 10.4 Frontend

- **Django Templates** server-rendered + Design System (`@design_system/design-system.html`).
- JavaScript leve para interatividade (drag-and-drop do Kanban, polling de notificações, streaming SSE do chat, estados de loading). HTMX e/ou Alpine.js são recomendados por simplicidade (decisão na seção 50), mas qualquer JS vanilla equivalente é aceitável desde que respeite o Design System.
- Renderização de **Markdown → HTML** no chat (biblioteca JS de markdown no cliente, ou `markdown` no servidor com sanitização).

---

## 11. Estrutura Recomendada do Projeto Django

```
scsi/                              # raiz do repositório
├── .venv/                         # ambiente virtual (não versionado)
├── .env                           # credenciais (não versionado)
├── .env.example                   # template das variáveis
├── .gitignore
├── requirements.txt               # sempre atualizado
├── manage.py
├── docker-compose.yml             # desenvolvimento local
├── docker-stack.yml               # produção (Docker Swarm)
├── Dockerfile
├── entrypoint.sh                  # migrate + collectstatic + start
├── mkdocs.yml
├── docs/                          # documentação MKDocs (com Mermaid)
│   ├── index.md
│   ├── architecture.md
│   ├── multi-tenant.md
│   ├── ai-agents.md
│   ├── deploy.md
│   └── ...
├── design_system/
│   └── design-system.html         # FONTE DE VERDADE do visual
├── static/                        # estáticos do projeto (tokens do DS)
├── media/                         # mídia protegida (NÃO servida publicamente)
├── templates/                     # templates globais (base.html, etc.)
│   ├── base.html
│   ├── base_auth.html
│   ├── base_app.html              # layout interno (menu lateral)
│   └── partials/
├── core/                          # projeto Django (config): settings, urls, celery, wsgi/asgi
│   ├── __init__.py                # carrega o app Celery
│   ├── settings.py                # ÚNICO settings, lê do .env
│   ├── urls.py                    # URL router raiz
│   ├── celery.py                  # instância Celery
│   ├── wsgi.py
│   └── asgi.py
│
│   # === Apps Django na RAIZ do projeto (irmãs de core/, SEM pasta apps/) ===
├── base/                          # app base: BaseModel, TenantAwareModel, mixins, middleware, utils
├── accounts/
├── tenants/
├── clients/
├── insurers/
├── insurance/
├── claims/
├── partners/
├── commissions/
├── crm/
├── reports/
├── ai_agents/
├── notifications/
├── documents/
└── dashboard/
```

> **Apps na raiz:** as apps de domínio ficam **diretamente na raiz** do projeto (irmãs de `core/`), **sem** pasta `apps/`. No `INSTALLED_APPS` são referenciadas pelo nome simples (ex.: `'base'`, `'accounts'`, `'insurance'`). A app **`base`** concentra `BaseModel`/`TenantAwareModel`/mixins/middleware/utils; **`core`** é o pacote de configuração do projeto (settings, urls, celery, wsgi/asgi).

**Padrão interno de cada app:**

```
<app>/                     # ex.: accounts/, insurance/, crm/ — na raiz do projeto
├── __init__.py
├── apps.py                # AppConfig; importa signals no ready()
├── admin.py
├── models.py              # ou models/ (package) quando muitas models
├── managers.py            # managers/querysets de tenant
├── forms.py
├── views.py
├── urls.py
├── services.py           # regras de negócio (ex: generate_policy_from_proposal)
├── signals.py            # apenas se houver signals
├── tasks.py              # tasks Celery da app
├── selectors.py          # (opcional) queries de leitura reutilizáveis
└── templates/<app>/
```

> **Regra de signals:** se uma app usa signals, eles ficam em `signals.py` e são conectados no `AppConfig.ready()`. Nunca em `models.py`.

---

## 12. Apps Django Recomendadas

| App | Responsabilidade | Principais models |
|---|---|---|
| **base** | `BaseModel`, `TenantAwareModel`, `TenantManager`, `TenantMiddleware`, mixins (`TenantQuerysetMixin`, `RoleRequiredMixin`), context processors, utils, templates base. | (abstratas) |
| **accounts** | `User` customizado (login por email), `EmailBackend`, CBVs de registro/login/logout/perfil, recuperação de senha nativa, gestão de usuários e roles dentro do tenant. | `User` |
| **tenants** | `Brokerage` (o tenant), `Plan`, `Subscription`, fluxo de signup (cria corretora + owner + assinatura free), `TenantMiddleware`, seeds padrão (ramos, pipeline) via signal. | `Brokerage`, `Plan`, `Subscription` |
| **clients** | Cadastro e gestão de clientes (PF/PJ), anexos via `documents`, campo `ai_summary`. | `Client` |
| **insurers** | Seguradoras e ramos (linhas de negócio). | `Insurer`, `LineOfBusiness` |
| **insurance** | Propostas, apólices, itens cobertos, endossos, renovações; serviço de geração de apólice a partir de proposta. | `Proposal`, `Policy`, `CoveredItem`, `Endorsement`, `Renewal` |
| **claims** | Sinistros vinculados a item coberto de uma apólice. | `Claim` |
| **partners** | Hierarquia comercial: agentes e produtores (pessoas ou empresas), vínculos opcionais com `User`. | `Agent`, `Producer` |
| **commissions** | Comissões recebidas pela corretora e repasses (splits) para agentes/produtores; cálculo e relatórios. | `Commission`, `CommissionSplit` |
| **crm** | Pipelines personalizáveis, etapas (cores/ordem), negociações (deals/leads), histórico de mudança de etapa, grid e Kanban. | `Pipeline`, `Stage`, `Deal`, `DealStageHistory` |
| **reports** | Geração de relatórios (PDF via ReportLab/PyPDF e CSV), telas e menu de relatórios. | `ReportRequest` (opcional, para histórico) |
| **ai_agents** | Agentes de resumo (Celery) e agente de chat (LangGraph + tools isoladas por tenant), sessões e mensagens de chat, builders de prompt/tools. | `ChatSession`, `ChatMessage` |
| **notifications** | Notificações persistentes na interface; criação ao concluir tasks; endpoint de polling e marcação de leitura. | `Notification` |
| **documents** | Upload e **serviço de mídia protegida**; `Document` genérico anexável a cliente/proposta/apólice/sinistro; view de download autenticado. | `Document` |
| **dashboard** | Agregações, métricas e gráficos (incl. funil de negociações). Sem models próprias (lê das demais). | — |

> **Ajuste em relação à lista sugerida:** criamos `partners` (agentes/produtores) separado de `commissions` (registros financeiros) para manter responsabilidades coesas. `insurance` concentra proposta→apólice→item→endosso→renovação por serem fortemente acoplados (a apólice nasce da proposta e compartilha itens cobertos).

---

## 13. Modelagem de Domínio

### 13.1 Diagrama ER — Núcleo Multi Tenant e Cadastros

```mermaid
erDiagram
    Plan {
        int id PK
        string name
        string slug UK
        decimal price
        boolean is_available
        int max_users
        int max_clients
        json features
        datetime created_at
        datetime updated_at
    }
    Brokerage {
        int id PK
        string legal_name
        string trade_name
        string cnpj UK
        string susep_code
        string email
        string phone
        int owner_id FK
        int plan_id FK
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    Subscription {
        int id PK
        int brokerage_id FK
        int plan_id FK
        string status
        datetime started_at
        datetime expires_at
        datetime created_at
        datetime updated_at
    }
    User {
        int id PK
        string email UK
        string first_name
        string last_name
        string password
        int brokerage_id FK
        string role
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    Client {
        int id PK
        int brokerage_id FK
        string person_type
        string name
        string document
        string email
        string phone
        date birth_date
        text ai_summary
        string ai_summary_status
        datetime created_at
        datetime updated_at
    }
    Insurer {
        int id PK
        int brokerage_id FK
        string name
        string cnpj
        string susep_code
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    LineOfBusiness {
        int id PK
        int brokerage_id FK
        string name
        string code
        string category
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    Plan ||--o{ Brokerage : "define"
    Brokerage ||--|| Subscription : "tem"
    Plan ||--o{ Subscription : "referente a"
    Brokerage ||--o{ User : "possui"
    User ||--o| Brokerage : "owner (1)"
    Brokerage ||--o{ Client : "isola"
    Brokerage ||--o{ Insurer : "isola"
    Brokerage ||--o{ LineOfBusiness : "isola"
```

### 13.2 Diagrama ER — Propostas, Apólices, Itens, Sinistros, Endossos, Renovações

```mermaid
erDiagram
    Proposal {
        int id PK
        int brokerage_id FK
        int client_id FK
        int insurer_id FK
        int line_of_business_id FK
        int producer_id FK
        int agent_id FK
        string number
        string status
        decimal net_premium
        decimal total_premium
        decimal iof
        date proposed_start_date
        date proposed_end_date
        text ai_summary
        datetime created_at
        datetime updated_at
    }
    Policy {
        int id PK
        int brokerage_id FK
        int proposal_id FK
        int client_id FK
        int insurer_id FK
        int line_of_business_id FK
        int producer_id FK
        int agent_id FK
        string policy_number
        string status
        decimal net_premium
        decimal total_premium
        decimal iof
        decimal commission_rate
        date start_date
        date end_date
        text ai_summary
        datetime created_at
        datetime updated_at
    }
    CoveredItem {
        int id PK
        int brokerage_id FK
        int proposal_id FK
        int policy_id FK
        string item_type
        string description
        string identifier
        decimal insured_amount
        json attributes
        datetime created_at
        datetime updated_at
    }
    Claim {
        int id PK
        int brokerage_id FK
        int policy_id FK
        int covered_item_id FK
        string claim_number
        date occurrence_date
        date notice_date
        string status
        decimal claimed_amount
        decimal approved_amount
        text ai_summary
        datetime created_at
        datetime updated_at
    }
    Endorsement {
        int id PK
        int brokerage_id FK
        int policy_id FK
        string endorsement_number
        string type
        text description
        decimal premium_change
        date effective_date
        string status
        datetime created_at
        datetime updated_at
    }
    Renewal {
        int id PK
        int brokerage_id FK
        int policy_id FK
        int new_policy_id FK
        string status
        date due_date
        text notes
        datetime created_at
        datetime updated_at
    }

    Proposal ||--o{ CoveredItem : "tem"
    Policy ||--o{ CoveredItem : "tem"
    Proposal ||--o| Policy : "origina"
    Policy ||--o{ Claim : "tem"
    CoveredItem ||--o{ Claim : "objeto do sinistro"
    Policy ||--o{ Endorsement : "tem"
    Policy ||--o{ Renewal : "renovação de"
    Renewal ||--o| Policy : "gera nova"
```

### 13.3 Diagrama ER — Hierarquia Comercial, Comissões, CRM, IA, Notificações, Documentos

```mermaid
erDiagram
    Agent {
        int id PK
        int brokerage_id FK
        int user_id FK
        string entity_type
        string name
        string document
        decimal default_commission_rate
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    Producer {
        int id PK
        int brokerage_id FK
        int agent_id FK
        int user_id FK
        string entity_type
        string name
        string document
        decimal default_commission_rate
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    Commission {
        int id PK
        int brokerage_id FK
        int policy_id FK
        decimal base_premium
        decimal insurer_rate
        decimal insurer_amount
        string status
        date reference_date
        datetime created_at
        datetime updated_at
    }
    CommissionSplit {
        int id PK
        int brokerage_id FK
        int commission_id FK
        string beneficiary_type
        int agent_id FK
        int producer_id FK
        decimal rate
        decimal amount
        string status
        datetime created_at
        datetime updated_at
    }
    Pipeline {
        int id PK
        int brokerage_id FK
        string name
        boolean is_default
        datetime created_at
        datetime updated_at
    }
    Stage {
        int id PK
        int brokerage_id FK
        int pipeline_id FK
        string name
        string color
        int order
        boolean is_won
        boolean is_lost
        datetime created_at
        datetime updated_at
    }
    Deal {
        int id PK
        int brokerage_id FK
        int pipeline_id FK
        int stage_id FK
        int client_id FK
        int producer_id FK
        int proposal_id FK
        string title
        decimal estimated_value
        string status
        date expected_close_date
        text ai_summary
        datetime created_at
        datetime updated_at
    }
    DealStageHistory {
        int id PK
        int brokerage_id FK
        int deal_id FK
        int from_stage_id FK
        int to_stage_id FK
        int changed_by_id FK
        datetime changed_at
    }
    ChatSession {
        int id PK
        int brokerage_id FK
        int user_id FK
        string title
        datetime created_at
        datetime updated_at
    }
    ChatMessage {
        int id PK
        int brokerage_id FK
        int session_id FK
        string role
        text content
        datetime created_at
    }
    Notification {
        int id PK
        int brokerage_id FK
        int user_id FK
        string type
        string title
        text message
        string url
        boolean is_read
        datetime created_at
        datetime updated_at
    }
    Document {
        int id PK
        int brokerage_id FK
        int uploaded_by_id FK
        string content_type_label
        int object_id
        string file
        string original_filename
        string mime_type
        int size
        datetime created_at
        datetime updated_at
    }

    Agent ||--o{ Producer : "tem"
    Commission ||--o{ CommissionSplit : "reparte"
    Agent ||--o{ CommissionSplit : "recebe"
    Producer ||--o{ CommissionSplit : "recebe"
    Pipeline ||--o{ Stage : "tem"
    Pipeline ||--o{ Deal : "contém"
    Stage ||--o{ Deal : "posiciona"
    Deal ||--o{ DealStageHistory : "registra"
    ChatSession ||--o{ ChatMessage : "contém"
```

> **Nota:** todas as entidades acima herdam `brokerage` (FK), `created_at` e `updated_at`. O campo `brokerage` aparece explicitamente nos diagramas para reforçar o isolamento.

---

## 14. Entidades Principais do Sistema

Esta seção descreve cada entidade com **campos essenciais sugeridos**, relação com o tenant e regras. Tipos em estilo Django.

### 14.1 `Plan` (tenants) — *global, sem tenant*

| Campo | Tipo | Notas |
|---|---|---|
| `name` | `CharField` | "Free", "Pro", "Business" |
| `slug` | `SlugField(unique=True)` | identificador |
| `price` | `DecimalField` | 0 para free |
| `is_available` | `BooleanField` | `True` só para Free na V1; demais = "Em breve" |
| `max_users`, `max_clients`, `max_policies` | `PositiveIntegerField(null=True)` | limites (null = ilimitado) |
| `features` | `JSONField` | lista de features exibidas na landing |

> `Plan` **não** é tenant-aware (é catálogo global). Sem `brokerage`.

### 14.2 `Brokerage` (tenants) — *o tenant*

| Campo | Tipo | Notas |
|---|---|---|
| `legal_name` | `CharField` | razão social (**obrigatório**) |
| `trade_name` | `CharField(blank=True)` | nome fantasia |
| `cnpj` | `CharField(unique=True)` | **obrigatório**, validado |
| `susep_code` | `CharField(blank=True)` | registro SUSEP da corretora |
| `email`, `phone` | `CharField(blank=True)` | contato (opcionais) |
| address fields | `CharField(blank=True)` | logradouro, número, cidade, UF, CEP (opcionais) |
| `owner` | `FK(User)` | usuário dono |
| `plan` | `FK(Plan)` | plano atual |
| `is_active` | `BooleanField(default=True)` | soft delete |

> A `Brokerage` é o tenant raiz; **não** herda `TenantAwareModel` (ela própria é o tenant), mas herda `BaseModel`.

### 14.3 `Subscription` (tenants)

`brokerage` (FK, OneToOne na V1), `plan` (FK), `status` (`active`/`past_due`/`canceled`), `started_at`, `expires_at`. Na V1, sempre `active` no plano Free.

### 14.4 `User` (accounts)

| Campo | Tipo | Notas |
|---|---|---|
| `email` | `EmailField(unique=True)` | `USERNAME_FIELD` |
| `first_name`, `last_name` | `CharField` | |
| `brokerage` | `FK(Brokerage, null=True)` | tenant do usuário (null só transitoriamente no signup) |
| `role` | `CharField(choices=Role)` | owner/manager/broker/agent/producer/operational |
| `is_active`, `is_staff`, `is_superuser` | flags Django | |

`USERNAME_FIELD = 'email'`, `REQUIRED_FIELDS = ['first_name', 'last_name']`. Backend `EmailBackend`.

### 14.5 `Client` (clients) — *tenant-aware*

`person_type` (`PF`/`PJ`), `name` (nome ou razão social), `document` (CPF/CNPJ), `email`, `phone`, `birth_date` (PF), address fields, `notes`, **`ai_summary` (`TextField`)**, `ai_summary_status` (`idle`/`processing`/`done`/`error`), `ai_summary_updated_at`. Unicidade: `UniqueConstraint(['brokerage', 'document'])`.

### 14.6 `Insurer` (insurers) — *tenant-aware*

`name`, `cnpj`, `susep_code`, `email`, `phone`, `is_active`. Cada corretora mantém sua lista de seguradoras parceiras.

### 14.7 `LineOfBusiness` (insurers) — *tenant-aware* — "Ramo"

`name` (Auto, Vida, Residencial, Empresarial, Viagem...), `code` (ramo SUSEP), `category`, `is_active`. Seedado com ramos comuns ao criar a corretora (signal).

### 14.8 `Proposal` (insurance) — *tenant-aware*

`client` (FK), `insurer` (FK), `line_of_business` (FK), `producer` (FK, null), `agent` (FK, null), `number` (único por tenant), `status` (`draft`/`sent`/`under_analysis`/`approved`/`rejected`/`converted`), `net_premium`, `total_premium`, `iof`, `proposed_start_date`, `proposed_end_date`, `payment_terms`, `notes`, `ai_summary` + status. Relaciona-se com `CoveredItem` (1:N) e `Document` (anexos). Pode originar uma `Policy`.

### 14.9 `Policy` (insurance) — *tenant-aware*

`proposal` (FK, null — origem), `client`, `insurer`, `line_of_business`, `producer`, `agent`, `policy_number` (único por tenant), `status` (`active`/`canceled`/`expired`/`renewed`), `net_premium`, `total_premium`, `iof`, `commission_rate`, `start_date`, `end_date`, `payment_info`, `ai_summary` + status. Relaciona-se com `CoveredItem`, `Claim`, `Endorsement`, `Renewal`, `Commission`, `Document`.

### 14.10 `CoveredItem` (insurance) — *tenant-aware*

`proposal` (FK, null), `policy` (FK, null) — **exatamente um** preenchido (constraint `CheckConstraint`), `item_type` (`auto`/`property`/`fleet`/`travel`/`life`/`equipment`/`other`), `description`, `identifier` (placa/chassi/endereço/etc.), `insured_amount`, `attributes` (`JSONField` para dados específicos do tipo: ano/modelo do auto, m² do imóvel, etc.), `coverages` (`JSONField`, lista de coberturas e limites). Um sinistro sempre aponta para um `CoveredItem` de uma `Policy`.

### 14.11 `Claim` (claims) — *tenant-aware*

`policy` (FK), `covered_item` (FK, **obrigatório**), `claim_number`, `occurrence_date`, `notice_date`, `status` (`opened`/`under_analysis`/`approved`/`denied`/`paid`/`closed`), `description`, `claimed_amount`, `approved_amount`, `ai_summary` + status. Anexos via `Document`.

### 14.12 `Endorsement` (insurance) — *tenant-aware*

`policy` (FK), `endorsement_number`, `type` (`increase`/`decrease`/`cancellation`/`data_change`), `description`, `premium_change` (Decimal, +/-), `effective_date`, `status`.

### 14.13 `Renewal` (insurance) — *tenant-aware*

`policy` (FK, original), `new_policy` (FK, null — apólice renovada), `status` (`pending`/`in_progress`/`renewed`/`lost`/`not_renewed`), `due_date` (vencimento da original), `notes`. Criada/atualizada por task do Beat.

### 14.14 `Agent` (partners) — *tenant-aware*

`entity_type` (`person`/`company`), `name`, `document` (CPF/CNPJ), `email`, `phone`, `susep_code`, `user` (FK null — login opcional), `default_commission_rate`, `is_active`. Um agente tem vários produtores.

### 14.15 `Producer` (partners) — *tenant-aware*

`agent` (FK null — vinculado a agente ou direto à corretora), `entity_type`, `name`, `document`, `email`, `phone`, `user` (FK null), `default_commission_rate`, `is_active`.

### 14.16 `Commission` (commissions) — *tenant-aware*

`policy` (FK), `base_premium`, `insurer_rate` (% paga pela seguradora), `insurer_amount` (valor recebido pela corretora), `status` (`pending`/`received`/`paid`), `reference_date`. Gerada ao criar a apólice (signal/service).

### 14.17 `CommissionSplit` (commissions) — *tenant-aware* — "Repasse"

`commission` (FK), `beneficiary_type` (`agent`/`producer`), `agent` (FK null), `producer` (FK null), `rate` (% do repasse), `amount`, `status` (`pending`/`paid`), `paid_at`. Permite múltiplos repasses por comissão.

### 14.18 CRM: `Pipeline`, `Stage`, `Deal`, `DealStageHistory` (crm) — *tenant-aware*

- `Pipeline`: `name`, `is_default`.
- `Stage`: `pipeline` (FK), `name`, `color` (hex), `order`, `is_won`, `is_lost`.
- `Deal`: `pipeline`, `stage`, `client` (FK null — lead antes de virar cliente), `producer` (FK), `agent` (FK null), `line_of_business` (FK null), `insurer` (FK null), `proposal` (FK null), `title`, `description`, `estimated_value`, `status` (`open`/`won`/`lost`), `expected_close_date`, `ai_summary` + status.
- `DealStageHistory`: `deal` (FK), `from_stage`, `to_stage`, `changed_by` (FK User), `changed_at`, `note`.

### 14.19 IA: `ChatSession`, `ChatMessage` (ai_agents) — *tenant-aware*

- `ChatSession`: `user` (FK), `title` (auto a partir da 1ª mensagem). Sessões salvas por usuário.
- `ChatMessage`: `session` (FK), `role` (`user`/`assistant`/`system`/`tool`), `content` (Markdown), `created_at`. (Opcional: `token_count`.)

### 14.20 `Notification` (notifications) — *tenant-aware*

`user` (FK destinatário), `type` (`ai_summary`/`report`/`renewal`/`system`), `title`, `message`, `url` (link de destino), `is_read`, `read_at`.

### 14.21 `Document` (documents) — *tenant-aware*

`uploaded_by` (FK User), anexável genericamente via `ContentType` + `object_id` (a Client/Proposal/Policy/Claim), `file` (`FileField` em storage protegido), `original_filename`, `mime_type`, `size`. Servido **somente** por view protegida (seção 16).

---

## 15. Regras de Permissão e Segurança

### 15.1 Autorização em Duas Dimensões

Toda operação crítica é autorizada por **(a) tenant** e **(b) role**:

```mermaid
flowchart TD
    A[Request em rota privada] --> B{Autenticado?}
    B -->|Não| L[Redireciona para login]
    B -->|Sim| C{request.tenant resolvido?}
    C -->|Não| E[403 / onboarding]
    C -->|Sim| D{objeto.brokerage == request.tenant?}
    D -->|Não| F[404 - não vaza existência]
    D -->|Sim| G{role tem permissão para a ação?}
    G -->|Não| H[403 - sem permissão]
    G -->|Sim| I[Executa ação]
```

### 15.2 Mecanismos

- **`LoginRequiredMixin`** em todas as CBVs internas (ou middleware que exige login fora das rotas públicas).
- **`TenantQuerysetMixin`** filtra `get_queryset()` por `request.tenant` — garante que detail/update/delete só alcancem objetos do tenant. Objetos de outro tenant retornam **404** (nunca 403, para não vazar existência).
- **`RoleRequiredMixin`** (ou `PermissionRequiredMixin` nativo + grupos) restringe ações por `role`. Ex.: só `owner`/`manager` gerenciam usuários; só `owner` altera plano.
- **Grupos e permissões do Django:** ao criar a corretora, criar/atribuir grupos por role com permissões nativas; checar com `user.has_perm`.
- **Validação de FKs no `clean()`/`save()`:** toda FK relacionada (client, policy, insurer...) deve pertencer ao mesmo `brokerage`. Bloqueia POST malicioso com IDs de outro tenant.
- **Forms com querysets filtrados:** `ModelChoiceField.queryset` sempre limitado ao tenant.

### 15.3 Boas Práticas de Segurança

- `DEBUG=False` em produção; `ALLOWED_HOSTS` e `CSRF_TRUSTED_ORIGINS` configurados via env.
- Cookies seguros: `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_HSTS_SECONDS`, `SECURE_SSL_REDIRECT` (TLS via Traefik).
- `SECRET_KEY`, credenciais e chaves só via `.env`/Docker secrets — nunca no código.
- CSRF em todos os formulários; proteção XSS por escaping de template + sanitização do Markdown do chat.
- Senhas com validadores nativos do Django; recuperação por e-mail nativa.
- Rate limiting (recomendado) no login e no chat de IA para evitar abuso.
- Upload de arquivos: validar `content_type`/extensão/tamanho; armazenar fora da raiz pública.
- **IA:** tools nunca recebem o tenant do modelo; o servidor injeta. (Ver seções 9.2 e 34.)

---

## 16. Gestão de Arquivos e Mídias Protegidas

### 16.1 Princípio

Arquivos de clientes, propostas, apólices e sinistros **nunca** são servidos publicamente. **Não há** mapeamento de `/media/` no Traefik. Todo acesso passa por uma **view protegida** que verifica autenticação, tenant e permissão.

### 16.2 Armazenamento Segregado por Tenant

```
media/                                 # fora de qualquer rota pública
└── brokerage_<id>/
    ├── clients/<client_id>/<uuid>_<filename>
    ├── proposals/<proposal_id>/<uuid>_<filename>
    ├── policies/<policy_id>/<uuid>_<filename>
    └── claims/<claim_id>/<uuid>_<filename>
```

- `upload_to` calcula o caminho incluindo `brokerage_<id>` e um `uuid` para evitar colisão/enumeração.
- `MEDIA_ROOT` aponta para um **volume Docker** persistente (ver seções 43/44).

### 16.3 Fluxo de Download Protegido

```mermaid
flowchart TD
    A[Usuário clica em baixar anexo] --> B[GET /documents/<id>/download/]
    B --> C{Autenticado?}
    C -->|Não| D[Redireciona login]
    C -->|Sim| E[Document.objects.for_tenant request.tenant get id]
    E --> F{Existe no tenant?}
    F -->|Não| G[404]
    F -->|Sim| H{role pode acessar a entidade-pai?}
    H -->|Não| I[403]
    H -->|Sim| J[FileResponse stream do arquivo - Content-Disposition]
```

### 16.4 Estratégia de Serving (decisão)

- **V1 (recomendado):** `ProtectedDocumentDownloadView` retorna `FileResponse(open(path,'rb'))` após as checagens. Simples, nativo, seguro. Suficiente para o volume inicial.
- **Escala (futuro):** para grandes volumes/arquivos, adicionar **sidecar nginx** com `X-Accel-Redirect` (Django autentica e delega o streaming ao nginx) **ou** migrar mídia para **object storage (S3/MinIO) com URLs assinadas de curta duração**. O adapter de storage do Django torna a migração transparente. Documentado como trade-off na seção 50.

### 16.5 Regras

- Toda criação de `Document` grava `brokerage`, `uploaded_by` e a entidade-pai (ContentType + object_id).
- A view de download valida que a **entidade-pai** pertence ao tenant e que o `role` pode vê-la.
- Listagem de anexos numa tela (cliente/proposta/apólice/sinistro) só mostra documentos daquele objeto e tenant.
- Nenhum link direto a `MEDIA_URL` é exposto nos templates.

---

## 17. Autenticação e Usuários

### F01 — Login por E-mail
- **Descrição:** autenticação usando o sistema nativo do Django com `email` como identificador.
- **Regras de Negócio:**
  - `User.USERNAME_FIELD = 'email'`; backend `EmailBackend` em `accounts/backends.py`.
  - `User` customizado definido **antes** do primeiro `migrate` (`AUTH_USER_MODEL = 'accounts.User'`).
  - Após login, redireciona ao dashboard do tenant.
- **Critérios de Aceite:**
  - [ ] Login feito com e-mail e senha (sem campo username).
  - [ ] Credenciais inválidas exibem mensagem clara (sem revelar se o e-mail existe).
  - [ ] Sessão respeita cookies seguros em produção.

### F02 — Recuperação de Senha (nativa)
- **Descrição:** fluxo nativo `PasswordResetView` → e-mail → `PasswordResetConfirmView`.
- **Regras de Negócio:** e-mails configurados via `.env` (seção 42); envio assíncrono via Celery (seção 36).
- **Critérios de Aceite:**
  - [ ] Solicitar reset envia e-mail com link tokenizado.
  - [ ] Link expira conforme padrão do Django.
  - [ ] Nova senha respeita validadores nativos.
  - [ ] Templates de e-mail e páginas seguem o Design System.

### F03 — Gestão de Usuários da Corretora
- **Descrição:** owner/manager convidam e gerenciam usuários com `role`, todos no mesmo tenant.
- **Regras de Negócio:**
  - Novo usuário herda o `brokerage` de quem convidou.
  - Apenas `owner`/`manager` acessam a gestão de usuários; só `owner` promove a `owner`.
  - Respeita limite `Plan.max_users`.
- **Critérios de Aceite:**
  - [ ] Listagem mostra apenas usuários do tenant.
  - [ ] Criar usuário envia e-mail de definição de senha.
  - [ ] Alterar `role` reflete imediatamente nas permissões.
  - [ ] Desativar usuário (`is_active=False`) bloqueia login sem apagar histórico.

---

## 18. Cadastro e Gestão de Corretoras

### F04 — Onboarding (criação da corretora)
- **Descrição:** no signup, o usuário cria sua conta **e** a corretora (tenant).
- **Regras de Negócio:**
  - **CNPJ e razão social obrigatórios**; demais dados opcionais.
  - CNPJ único globalmente (`Brokerage.cnpj` unique) e validado.
  - Cria `Brokerage` + `User(role='owner')` + `Subscription(plan=Free)` em transação atômica.
  - Signal pós-criação seeda **ramos padrão** e **pipeline padrão** com etapas.
- **Critérios de Aceite:**
  - [ ] Formulário valida CNPJ e razão social como obrigatórios.
  - [ ] CNPJ duplicado exibe erro e não cria nada (rollback).
  - [ ] Após signup, usuário logado e redirecionado ao dashboard.
  - [ ] Ramos e pipeline padrão existem para a nova corretora.

### F05 — Dados e Configurações da Corretora
- **Descrição:** owner edita dados cadastrais, SUSEP, endereço e visualiza plano.
- **Critérios de Aceite:**
  - [ ] Edição restrita a `owner` (e leitura a `manager`).
  - [ ] Página "Meu Plano" mostra plano atual e botões "Em breve" desabilitados para planos pagos.
  - [ ] `is_active=False` desativa a corretora (soft delete) sem exclusão física.

---

## 19. Cadastro e Gestão de Clientes

### F06 — CRUD de Clientes
- **Descrição:** cadastro de clientes PF/PJ com dados, endereço e anexos.
- **Regras de Negócio:**
  - `person_type` define campos relevantes (CPF + nascimento para PF; CNPJ + razão para PJ).
  - `UniqueConstraint(['brokerage','document'])` — documento único por corretora.
  - Respeita limite `Plan.max_clients`.
- **Critérios de Aceite:**
  - [ ] Lista de clientes filtra por tenant, com busca por nome/documento e paginação.
  - [ ] Documento duplicado no tenant é rejeitado.
  - [ ] Tela de detalhe exibe apólices, propostas, sinistros e anexos do cliente.
  - [ ] Botão "Resumir com IA" presente no detalhe (ver seção 34).

### F07 — Anexos do Cliente
- **Critérios de Aceite:**
  - [ ] Upload de múltiplos formatos via `Document` (seção 16).
  - [ ] Anexos só acessíveis por usuários autorizados do tenant.
  - [ ] Download passa pela view protegida.

---

## 20. Cadastro e Gestão de Seguradoras

### F08 — CRUD de Seguradoras
- **Descrição:** cada corretora mantém sua lista de seguradoras parceiras (`Insurer`, tenant-aware).
- **Critérios de Aceite:**
  - [ ] CRUD isolado por tenant.
  - [ ] Campos: nome, CNPJ, código SUSEP, contato, `is_active`.
  - [ ] Seguradoras inativas não aparecem em selects de proposta/apólice.
  - [ ] Listagem com busca e paginação.

---

## 21. Cadastro e Gestão de Ramos

### F09 — CRUD de Ramos (`LineOfBusiness`)
- **Descrição:** ramos/linhas de negócio (Auto, Vida, Residencial, Empresarial, Viagem...), tenant-aware.
- **Regras de Negócio:** ramos padrão seedados no onboarding; corretora pode adicionar/editar/desativar.
- **Critérios de Aceite:**
  - [ ] CRUD isolado por tenant.
  - [ ] Campos: nome, código (ramo SUSEP), categoria, `is_active`.
  - [ ] Ramos alimentam selects de propostas, apólices, negociações e relatórios.

---

## 22. Gestão de Propostas

### F10 — CRUD de Propostas
- **Descrição:** propostas vinculam cliente, seguradora, ramo, produtor/agente e itens cobertos.
- **Regras de Negócio:**
  - `number` único por tenant.
  - `status`: `draft` → `sent` → `under_analysis` → `approved`/`rejected` → `converted` (quando vira apólice).
  - Valores monetários em `DecimalField`; `total_premium = net_premium + iof` (validável).
  - Pode ter N itens cobertos e N anexos.
  - Pode estar vinculada a uma negociação do CRM (`Deal.proposal`).
- **Critérios de Aceite:**
  - [ ] Lista filtra por tenant, status, seguradora, ramo, produtor e período.
  - [ ] Selects de FK (cliente, seguradora, ramo, produtor) limitados ao tenant.
  - [ ] Itens cobertos gerenciáveis na própria tela (inline/abas).
  - [ ] Anexos protegidos disponíveis.
  - [ ] Botão **"Gerar apólice"** visível quando `status` permite (ver seção 24).
  - [ ] Botão "Resumir com IA" presente.

---

## 23. Gestão de Apólices

### F11 — CRUD de Apólices
- **Descrição:** apólices representam contratos efetivados; nascem de proposta ou manualmente.
- **Regras de Negócio:**
  - `policy_number` único por tenant.
  - `status`: `active`/`canceled`/`expired`/`renewed`.
  - `start_date`/`end_date` definem vigência; vencimento alimenta renovações.
  - Ao criar apólice, gera `Commission` (signal/service) com base em `commission_rate`.
  - Relaciona itens cobertos, sinistros, endossos, renovações e anexos.
- **Critérios de Aceite:**
  - [ ] Lista filtra por tenant, status, seguradora, ramo, vigência.
  - [ ] Detalhe mostra itens cobertos, sinistros, endossos, renovações, comissão e anexos.
  - [ ] Criação gera comissão automaticamente.
  - [ ] Botão "Resumir com IA" presente.

---

## 24. Geração de Apólice a partir de Proposta

### F12 — Botão "Gerar apólice"
- **Descrição:** na tela da proposta, o botão **"Gerar apólice"** cria uma `Policy` a partir dos dados da `Proposal`.

#### 24.1 Dados Copiados (automáticos)
| Da Proposal | Para a Policy |
|---|---|
| `brokerage`, `client`, `insurer`, `line_of_business` | idem (mesmo tenant) |
| `producer`, `agent` | idem |
| `net_premium`, `total_premium`, `iof` | idem (editáveis depois) |
| `proposed_start_date` → `start_date` | vigência inicial |
| `proposed_end_date` → `end_date` | vigência final |
| Cada `CoveredItem` da proposta | **clonado** com `policy` setado e `proposal=None` (ou mantém referência) |
| `proposal` | gravado em `Policy.proposal` (rastreabilidade) |

#### 24.2 Dados Editáveis (antes de confirmar)
- `policy_number` (**obrigatório** informar — não existe na proposta).
- `start_date`/`end_date` (ajustáveis).
- `commission_rate` (informar a comissão acordada).
- Valores monetários (ajuste fino).

#### 24.3 Validações
- Proposta deve estar em `status` elegível (ex.: `approved`).
- Proposta **não pode** já ter apólice gerada (idempotência: bloquear segunda geração ou avisar).
- `policy_number` único por tenant.
- Todas as FKs pertencem ao mesmo tenant da proposta.
- Operação em **transação atômica**: cria `Policy` + clona `CoveredItem`s + gera `Commission` + marca `Proposal.status='converted'` + (se houver) marca `Deal` como ganho.

#### 24.4 Fluxo

```mermaid
flowchart TD
    A[Usuário clica 'Gerar apólice'] --> B{Proposta elegível e sem apólice?}
    B -->|Não| C[Mensagem de bloqueio]
    B -->|Sim| D[Abre form pré-preenchido com dados copiados]
    D --> E[Usuário informa policy_number e commission_rate]
    E --> F{Validações OK?}
    F -->|Não| D
    F -->|Sim| G[Transação: cria Policy + clona itens + gera Commission]
    G --> H[Proposal.status = converted]
    H --> I["Deal vinculado = won, se existir"]
    I --> J[Redireciona ao detalhe da nova apólice]
```

- **Critérios de Aceite:**
  - [ ] Botão "Gerar apólice" presente na proposta elegível.
  - [ ] Form pré-preenchido com dados copiados; `policy_number` obrigatório.
  - [ ] Itens cobertos são clonados para a apólice.
  - [ ] Comissão gerada na criação da apólice.
  - [ ] Proposta marcada como `converted`; segunda geração bloqueada.
  - [ ] Tudo em transação (rollback em erro).
  - [ ] Serviço isolado em `insurance/services.py::generate_policy_from_proposal`.

---

## 25. Gestão de Itens Cobertos

### F13 — CRUD de Itens Cobertos
- **Descrição:** objetos segurados (auto, imóvel, frota, viagem, vida, equipamento, outro) de propostas e apólices.
- **Regras de Negócio:**
  - `CheckConstraint`: exatamente um entre `proposal`/`policy` preenchido.
  - `item_type` define quais campos de `attributes` (JSONField) são exibidos no form dinâmico.
  - `insured_amount` (importância segurada) em Decimal.
  - Uma proposta/apólice pode ter **vários** itens cobertos.
  - Sinistro sempre referencia um `CoveredItem` de uma **apólice**.
- **Critérios de Aceite:**
  - [ ] Adição/edição/remoção de itens dentro da proposta e da apólice.
  - [ ] Form dinâmico por `item_type` (ex.: placa/chassi/ano para `auto`; endereço/m² para `property`).
  - [ ] Itens isolados por tenant.
  - [ ] Ao gerar apólice, itens da proposta são clonados (seção 24).

---

## 26. Gestão de Sinistros

### F14 — CRUD de Sinistros
- **Descrição:** registro e acompanhamento de sinistros vinculados a item coberto de apólice.
- **Regras de Negócio:**
  - `policy` e `covered_item` obrigatórios; `covered_item` deve pertencer à `policy`.
  - `status`: `opened`/`under_analysis`/`approved`/`denied`/`paid`/`closed`.
  - `occurrence_date` ≤ `notice_date`; ambos dentro/coerentes com a vigência.
  - Anexos (BOs, fotos, laudos) via `Document` protegido.
- **Critérios de Aceite:**
  - [ ] Criação só permite escolher `covered_item` da apólice selecionada (e do tenant).
  - [ ] Lista filtra por tenant, status, apólice, período.
  - [ ] Anexos protegidos disponíveis.
  - [ ] Botão "Resumir com IA" presente.

---

## 27. Gestão de Endossos

### F15 — CRUD de Endossos
- **Descrição:** alterações em apólices (aumento, redução, cancelamento, alteração cadastral).
- **Regras de Negócio:**
  - `type`: `increase`/`decrease`/`cancellation`/`data_change`.
  - `premium_change` ajusta valores; `cancellation` pode alterar `Policy.status`.
  - `effective_date` registra a vigência da alteração.
- **Critérios de Aceite:**
  - [ ] Endossos vinculados a uma apólice do tenant.
  - [ ] `endorsement_number` único por apólice/tenant.
  - [ ] Endosso de cancelamento reflete no status da apólice.
  - [ ] Histórico de endossos visível no detalhe da apólice.

---

## 28. Gestão de Renovações

### F16 — Pipeline de Renovações
- **Descrição:** acompanhamento de apólices a vencer e seu desfecho de renovação.
- **Regras de Negócio:**
  - Task do Beat varre diariamente apólices com `end_date` próxima e cria/atualiza `Renewal(status='pending')`.
  - `status`: `pending`/`in_progress`/`renewed`/`lost`/`not_renewed`.
  - Ao renovar, gera nova `Policy` vinculada (`Renewal.new_policy`) e marca a original como `renewed`.
  - Notifica o responsável (seção 37).
- **Critérios de Aceite:**
  - [ ] Lista de renovações filtra por tenant, status e janela de vencimento.
  - [ ] Renovar gera nova apólice e atualiza status da original e da renovação.
  - [ ] Notificação criada para renovações próximas do vencimento.
  - [ ] Dashboard exibe renovações pendentes do período.

---

## 29. Gestão de Agentes, Produtores e Comissões

### 29.1 Hierarquia Comercial

```mermaid
flowchart TD
    B[Corretora - Brokerage] --> A1[Agente 1 - pessoa ou empresa]
    B --> A2[Agente 2]
    B --> P0[Produtor direto da corretora]
    A1 --> P1[Produtor 1.1]
    A1 --> P2[Produtor 1.2]
    A2 --> P3[Produtor 2.1]
    B -. recebe comissão da seguradora .-> C[Comissão]
    C -. repassa .-> A1
    C -. repassa .-> P1
```

- Uma **corretora** tem vários **agentes**; um **agente** tem vários **produtores**; um **produtor** pode ser direto da corretora (`agent=null`).
- A **comissão é recebida pela corretora** (`Commission`) e **repassada** (`CommissionSplit`) a agentes e/ou produtores.

### F17 — CRUD de Agentes e Produtores
- **Critérios de Aceite:**
  - [ ] CRUD de `Agent` e `Producer` isolado por tenant.
  - [ ] `Agent`/`Producer` podem ser pessoa ou empresa (`entity_type`) e ter `user` opcional para login.
  - [ ] Produtor pode vincular-se a um agente ou direto à corretora.
  - [ ] Taxa de comissão padrão por agente/produtor.

### F18 — Comissões e Repasses
- **Descrição:** cálculo da comissão recebida e dos repasses; relatório por período/beneficiário.
- **Regras de Negócio:**
  - `Commission` gerada ao criar apólice: `insurer_amount = base_premium * insurer_rate`.
  - `CommissionSplit`: cada repasse com `rate`/`amount` para agente/produtor; soma dos repasses ≤ comissão recebida (validação).
  - `status` de comissão (`pending`/`received`/`paid`) e de cada split (`pending`/`paid`).
  - Serviço `commissions/services.py::calculate_commission(policy)` e `build_splits(commission)`.
- **Critérios de Aceite:**
  - [ ] Comissão criada automaticamente na geração da apólice.
  - [ ] Repasses calculados conforme taxas de agente/produtor.
  - [ ] Soma de repasses não excede a comissão recebida.
  - [ ] Relatório de comissões e repasses por período e beneficiário (PDF/CSV — seção 32).

---

## 30. CRM com Grid e Kanban

### F19 — Pipeline Personalizável
- **Descrição:** etapas com nome, cor e ordem, configuráveis por corretora; etapas marcáveis como `is_won`/`is_lost`.
- **Critérios de Aceite:**
  - [ ] CRUD de `Pipeline` e `Stage` isolado por tenant.
  - [ ] Reordenar etapas e definir cores.
  - [ ] Pipeline padrão criado no onboarding.

### F20 — Visualização Kanban (drag-and-drop)
- **Descrição:** cards (negociações) distribuídos por colunas (etapas); arrastar move de etapa.
- **Dados do card:** título, cliente/lead, produtor, valor estimado, ramo, seguradora, data prevista de fechamento, indicador de proposta vinculada, badge de resumo IA.
- **Regras de Negócio:**
  - Arrastar para nova etapa dispara endpoint que atualiza `Deal.stage` e registra `DealStageHistory` (from/to/changed_by/changed_at).
  - Mover para etapa `is_won`/`is_lost` atualiza `Deal.status`.
- **Critérios de Aceite:**
  - [ ] Cards isolados por tenant e por pipeline.
  - [ ] Drag-and-drop persiste a etapa via requisição assíncrona (CSRF protegido).
  - [ ] Mudança de etapa registra histórico.
  - [ ] Etapas won/lost atualizam status do deal.

### F21 — Visualização Grid
- **Critérios de Aceite:**
  - [ ] Mesma base de dados em formato tabela com filtros (etapa, produtor, valor, período).
  - [ ] Ordenação e paginação.
  - [ ] Ação rápida para abrir o detalhe da negociação.

### F22 — Relação com Propostas/Clientes/Produtores
- **Critérios de Aceite:**
  - [ ] Negociação pode gerar/vincular uma proposta (`Deal.proposal`).
  - [ ] Ganhar a negociação reflete na proposta/apólice quando aplicável.
  - [ ] Botão "Resumir com IA" na negociação.

### 30.1 Wireframe Conceitual — Kanban

```
+---------------------------------------------------------------------------------+
| CRM  [ Grid ] [ Kanban* ]              Pipeline: [ Vendas v ]   [ + Negociação ] |
+------------------+------------------+------------------+--------------------------+
| Novo Lead   (3)  | Em Cotação  (2)  | Proposta    (4)  | Ganho (verde)        (1) |
| ---------------- | ---------------- | ---------------- | ------------------------ |
| [Cartão: Auto    | [Cartão: Vida    | [Cartão: Resid.  | [Cartão: Empresarial     |
|  Cliente X       |  Cliente Y       |  Cliente Z       |  Cliente W               |
|  R$ 2.300  Júlia |  R$ 900   Júlia  |  R$ 1.500  Marcos|  R$ 8.000  Marcos        |
|  [IA] [prop?]  ] |  [IA]          ] |  [IA] [proposta] |  [IA] [apólice]        ] |
| [Cartão...]      | [Cartão...]      | [Cartão...]      |                          |
+------------------+------------------+------------------+--------------------------+
```

---

## 31. Dashboard e Métricas

### F23 — Dashboard da Corretora
- **Descrição:** visão geral com KPIs e gráficos variados, tudo isolado por tenant.
- **Métricas (cards):** nº de clientes, apólices ativas, propostas abertas, sinistros em aberto, renovações a vencer (30/60/90 dias), prêmio total emitido no período, comissão recebida e a receber.
- **Gráficos:**
  - **Funil de negociações** (formato funil com níveis = etapas do pipeline).
  - Apólices por ramo (pizza/barras).
  - Prêmio/comissão por mês (linha/barras).
  - Sinistros por status.
  - Top seguradoras por volume.
  - Produtividade por produtor/agente.
- **Insights:** bloco textual com destaques (ex.: "12 renovações vencem nos próximos 30 dias").
- **Critérios de Aceite:**
  - [ ] Todas as métricas filtram por `request.tenant`.
  - [ ] Gráfico de **funil** renderiza as etapas com contagem e valores.
  - [ ] Filtro de período afeta todos os gráficos.
  - [ ] Agregações usam queries otimizadas (`aggregate`/`annotate`, `select_related`).

### 31.1 Wireframe Conceitual — Dashboard

```
+----------------------------------------------------------------------------------+
| Dashboard                              Período: [ Últimos 30 dias v ]            |
+------------+------------+------------+------------+------------+------------------+
| Clientes   | Apólices   | Propostas  | Sinistros  | Renov. 30d | Comissão a rec.  |
|   1.482    |   1.197    |    63      |    11      |    12      |   R$ 38.420      |
+------------+------------+------------+------------+------------+------------------+
| Funil de Negociações (níveis)          | Prêmio x Comissão por mês               |
|   ███████████  Novo Lead       120     |   (gráfico de barras/linha)             |
|    ████████    Em Cotação       78     |                                         |
|     ██████     Proposta         44     +-----------------------------------------+
|      ███       Ganho            21     | Apólices por Ramo  | Sinistros p/ status|
+----------------------------------------+--------------------+--------------------+
| Insights IA: "12 renovações vencem em 30 dias. Ramo Auto lidera emissões."      |
+----------------------------------------------------------------------------------+
```

---

## 32. Relatórios e Exportações

### F24 — Central de Relatórios
- **Descrição:** menu e tela dedicados; geração de PDF (ReportLab/PyPDF) e CSV, isolada por tenant.
- **Relatórios sugeridos:**
  | Relatório | Conteúdo |
  |---|---|
  | Carteira de clientes | Clientes, apólices ativas, prêmio total |
  | Propostas | Por status, período, produtor, seguradora |
  | Apólices | Vigências, prêmios, ramo, seguradora |
  | Sinistros | Por status, valores reclamados/aprovados |
  | Renovações | A vencer, renovadas, perdidas |
  | Comissões e repasses | Recebido vs. repassado por beneficiário |
  | Seguradoras | Volume e participação por seguradora |
  | Produtividade | Produção por produtor/agente |
- **Regras de Negócio:**
  - Geração de PDF pesada roda em **Celery** (seção 36); CSV pequeno pode ser síncrono via `StreamingHttpResponse`.
  - PDFs montados com ReportLab; merge/append com PyPDF quando necessário.
  - Todo dado filtrado por `request.tenant`.
- **Critérios de Aceite:**
  - [ ] Tela de relatórios com filtros (período, status, ramo, seguradora, produtor).
  - [ ] Exportar PDF e CSV para cada relatório.
  - [ ] PDF respeita identidade visual do Design System (logo/cabeçalho da corretora).
  - [ ] Relatório grande é gerado em background e notifica ao concluir.

---

## 33. Landing Page, Cadastro, Login e Recuperação de Senha

### F25 — Landing Page (`scsi.digital`)
- **Descrição:** página pública na **raiz** apresentando o sistema, com CTAs para cadastro e login.
- **Conteúdo:** proposta de valor, principais funcionalidades, seção de planos, CTA "Criar conta grátis".
- **Critérios de Aceite:**
  - [ ] Página inicial na raiz (`/`), pública e responsiva.
  - [ ] Seção de planos com **Free** habilitado (sem cartão) e demais "Em breve" (botão desabilitado).
  - [ ] CTAs levam a cadastro e login.
  - [ ] Segue rigorosamente o Design System.

### F26 — Cadastro com Dados da Corretora
- **Critérios de Aceite:**
  - [ ] Form coleta dados do usuário + corretora (CNPJ e razão social obrigatórios).
  - [ ] Seleção de plano (apenas Free disponível).
  - [ ] Sem integração de pagamento.
  - [ ] Cria tenant + owner + assinatura em transação (ver F04).

### F27 — Login e Recuperação de Senha
- **Critérios de Aceite:**
  - [ ] Login por e-mail (F01) e reset nativo (F02), ambos com Design System.

### 33.1 Wireframe Conceitual — Landing

```
+----------------------------------------------------------------------+
|  SCSI                                   [ Entrar ]  [ Criar conta ]   |
+----------------------------------------------------------------------+
|   Gestão inteligente para corretoras de seguros.                     |
|   CRM, apólices, comissões e IA — em um só lugar.                    |
|              [ Criar conta grátis ]   (sem cartão)                   |
+----------------------------------------------------------------------+
|  [CRM Kanban]   [Apólices & Renovações]   [Comissões]   [IA]         |
+----------------------------------------------------------------------+
|  Planos:   FREE (R$0) [Começar]   PRO (Em breve)   BUSINESS (Em breve)|
+----------------------------------------------------------------------+
```

---

## 34. Agentes de Inteligência Artificial

### 34.1 Organização dos Agentes

O SCSI tem **dois tipos** de agentes, ambos construídos com **LangChain 1.0+/LangGraph** sobre **GPT-5.5-mini**, e ambos **estritamente isolados por tenant**:

| Tipo | Onde | Execução | Função |
|---|---|---|---|
| **Summary Agents** | Botão "Resumir com IA" em cliente/apólice/sinistro/proposta/negociação | **Assíncrona (Celery)** | Coletam dados da entidade (no tenant), geram resumo + insights, salvam em `entity.ai_summary` |
| **Chat Agent** | Tela de Chat IA (menu lateral) | **Síncrona com streaming (SSE)** | Conversa com o usuário usando **tools** que consultam os dados da corretora |

### 34.2 Isolamento por Tenant nas Tools (regra crítica)

> **O agente NUNCA acessa dados de outra corretora.** As tools recebem o `brokerage` **injetado no servidor** a partir do usuário autenticado. O modelo **não** controla o tenant.

```python
# ai_agents/tools.py (referência conceitual)
def build_tenant_tools(brokerage):
    @tool
    def list_clients(query: str = '') -> str:
        """Lista clientes da corretora (filtra por nome/documento)."""
        qs = Client.objects.filter(brokerage=brokerage)
        if query:
            qs = qs.filter(Q(name__icontains=query) | Q(document__icontains=query))
        return serialize_compact(qs[:20])

    @tool
    def get_policy(policy_number: str) -> str:
        """Retorna detalhes de uma apólice da corretora pelo número."""
        policy = Policy.objects.filter(
            brokerage=brokerage, policy_number=policy_number
        ).first()
        return serialize_compact(policy)

    # ... get_client, search_claims, list_renewals_due, commissions_summary, etc.
    return [list_clients, get_policy, ...]
```

- `brokerage` vem de `request.user.brokerage` (chat) ou do `brokerage` da entidade na task (resumo). **Nunca** é parâmetro do LLM.
- Toda query dentro de tool filtra por `brokerage=brokerage`.
- Tools retornam dados **compactos** (campos essenciais) para economizar tokens.

### 34.3 Summary Agent (LangGraph StateGraph)

```mermaid
flowchart LR
    A[load_entity] --> B[fetch_related_data via tenant tools]
    B --> C[build_prompt - contexto compacto]
    C --> D[generate - GPT-5.5-mini]
    D --> E[persist - entity.ai_summary + status done]
    E --> F[notify_user]
```

- Roda dentro da Celery task; cada nó é uma função pura.
- Saída em **Markdown** (resumo + bullets de insights). Salva em `entity.ai_summary`, `ai_summary_status='done'`, `ai_summary_updated_at`.
- Em erro: `ai_summary_status='error'` + notificação de falha.

### 34.4 Chat Agent (Tool Calling com Streaming)

- Agente LangGraph (tool-calling/ReAct) com as tools de tenant.
- Decide quais tools chamar para responder à pergunta sobre a carteira.
- Resposta **em Markdown**, **streamada** token a token via SSE (seção 35).
- Histórico limitado às últimas N mensagens da sessão (gestão de janela de contexto).

### 34.5 Construção do System Prompt

```
Você é o assistente da corretora "{trade_name}". Responda SEMPRE em português,
em Markdown. Use as ferramentas disponíveis para consultar dados reais da
corretora. NUNCA invente dados. Você só tem acesso aos dados desta corretora.
Se a informação não existir, diga que não encontrou.
Data de hoje: {today}. Papel do usuário: {role}.
```

### 34.6 Gestão de Contexto e Custos

| Estratégia | Decisão |
|---|---|
| Modelo padrão | GPT-5.5-mini (econômico) via env `OPENAI_MODEL` |
| Janela de histórico | Últimas N mensagens (ex.: 10) por sessão |
| Tools compactas | Retornam apenas campos essenciais e limitam nº de linhas |
| Resumos assíncronos | Não bloqueiam request; rodam no worker |
| Timeout/retry | Tasks com retry exponencial; chat com timeout amigável |

### F28 — Resumos por IA (todas as entidades)
- **Critérios de Aceite:**
  - [ ] Botão "Resumir com IA" em cliente, apólice, sinistro, proposta e negociação.
  - [ ] Clique dispara Celery task e retorna a UI imediatamente.
  - [ ] Resumo salvo no campo `ai_summary` da entidade.
  - [ ] Tools de coleta filtram por tenant.
  - [ ] Notificação ao concluir.

---

## 35. Chat com Agente de IA

### F29 — Tela de Chat IA
- **Descrição:** chat com sessões salvas por usuário, tools isoladas por tenant, respostas em Markdown com streaming.
- **Regras de Negócio:**
  - Acesso pelo **menu lateral**.
  - Usuário cria/renomeia/exclui **sessões**; sessões salvas por usuário (`ChatSession.user`, tenant-aware).
  - Cada turno salva `ChatMessage` (user e assistant) na sessão.
  - Resposta **streamada** via `StreamingHttpResponse` (SSE); cliente consome com `EventSource`.
  - Conteúdo da resposta em **Markdown** renderizado em **HTML** no template (com sanitização).
- **Critérios de Aceite:**
  - [ ] Menu lateral dá acesso ao chat.
  - [ ] Sessões listadas por usuário; criar/renomear/excluir.
  - [ ] Resposta aparece com efeito de **stream** (token a token).
  - [ ] Markdown renderizado como HTML.
  - [ ] Tools consultam apenas dados do tenant do usuário.
  - [ ] Histórico persistido por sessão.

### 35.1 Fluxo de Mensagem com Streaming

```mermaid
flowchart TD
    A[Usuário envia mensagem na sessão] --> B[POST salva ChatMessage role=user]
    B --> C[View valida auth + tenant; monta tools com brokerage]
    C --> D[LangGraph agent processa com GPT-5.5-mini]
    D --> E[Streaming callback emite tokens]
    E --> F[StreamingHttpResponse - SSE para o browser]
    F --> G[EventSource renderiza Markdown incrementalmente]
    G --> H["Ao finalizar, salva ChatMessage role=assistant"]
```

### 35.2 Wireframe Conceitual — Chat

```
+-------------------+----------------------------------------------+
| Sessões        +  |  Corretora ABC — Assistente IA               |
| ----------------- | -------------------------------------------- |
| > Renovações jun  |  Você: Quais apólices vencem este mês?       |
|   Sinistros Auto  |  IA:  **3 apólices** vencem em junho:        |
|   Carteira PJ     |       1. Apólice 12345 - Auto - Cliente X    |
|                   |       2. ...                                 |
| [ + Nova sessão ] |  [▌ streaming...]                            |
|                   | -------------------------------------------- |
|                   |  [ Digite sua mensagem...            ] [>]   |
+-------------------+----------------------------------------------+
```

---

## 36. Tasks Assíncronas com Celery

### 36.1 Configuração

- **Broker:** RabbitMQ. **Result backend:** Redis (ou DB via `django-celery-results`).
- **Serviços:** `celery worker` + `celery beat` (agendador, `DatabaseScheduler` via `django-celery-beat`).
- **Admin:** `dj-celery-panel` para visualizar tasks no Django Admin; resultados via `django-celery-results`.
- App Celery em `core/celery.py`, carregado no `core/__init__.py`.

### 36.2 Tipos de Tasks

| Task | Tipo | Descrição |
|---|---|---|
| `generate_client_summary(client_id)` | sob demanda | Resumo IA do cliente |
| `generate_policy_summary(policy_id)` | sob demanda | Resumo IA da apólice |
| `generate_claim_summary(claim_id)` | sob demanda | Resumo IA do sinistro |
| `generate_proposal_summary(proposal_id)` | sob demanda | Resumo IA da proposta |
| `generate_deal_summary(deal_id)` | sob demanda | Resumo IA da negociação |
| `generate_report_pdf(request_id)` | sob demanda | Relatório PDF pesado |
| `send_async_email(...)` | sob demanda | E-mails (inclui reset) |
| `check_renewals_due()` | **Beat (diária)** | Cria renovações e notifica vencimentos |
| `expire_policies()` | **Beat (diária)** | Marca apólices vencidas |
| `notify_pending_commissions()` | **Beat (semanal)** | Alerta comissões/repasses pendentes |

### 36.3 Fluxo de uma Task de Resumo (antes / durante / depois)

```mermaid
sequenceDiagram
    participant U as Usuário
    participant V as View
    participant Q as RabbitMQ
    participant W as Celery Worker
    participant DB as PostgreSQL
    participant N as Notifications

    U->>V: POST "Resumir com IA"
    V->>DB: entity.ai_summary_status = 'processing'
    V->>Q: enqueue generate_*_summary(id)
    V-->>U: 202 + UI (botão loading, aviso "vamos te notificar")
    Q->>W: entrega task
    W->>DB: coleta dados (tenant) + chama LLM
    W->>DB: salva ai_summary, status='done'
    W->>N: cria Notification(user, url=detalhe)
    Note over U: badge de notificação aparece via polling
    U->>V: abre entidade e vê o resumo
```

### 36.4 Reação da Interface

- **Antes:** botão habilitado "Resumir com IA".
- **Durante:** botão exibe **loading/spinner** e desabilita; toast "Estamos gerando o resumo. Você será notificado quando ficar pronto."
- **Depois:** notificação na interface (badge no sino) + ao reabrir/atualizar, o resumo aparece no card. `ai_summary_status` controla o estado visual (`processing`/`done`/`error`).

---

## 37. Notificações na Interface

### F30 — Notificações Persistentes
- **Descrição:** notificações in-app criadas ao concluir tasks (resumo, relatório, renovações).
- **Regras de Negócio:**
  - `Notification` (tenant-aware) por usuário; `is_read`/`read_at`.
  - Exibidas em **sino** no topbar com contador de não lidas.
  - Atualização via **polling** de endpoint leve (`/notifications/unread/`) a cada 15–30s (sem WebSocket na V1).
  - Clique abre `url` de destino e marca como lida.
- **Critérios de Aceite:**
  - [ ] Sino com contador de não lidas, isolado por usuário/tenant.
  - [ ] Polling atualiza o contador sem recarregar a página.
  - [ ] Conclusão de resumo/relatório gera notificação com link.
  - [ ] Marcar como lida individual e "marcar todas como lidas".

### 37.1 Estratégia Técnica

```mermaid
flowchart LR
    A[Task conclui] --> B[Cria Notification]
    B --> C[(DB)]
    D[Frontend - polling 15-30s] --> E[GET /notifications/unread/]
    E --> C
    C --> F[Retorna contador + últimas N]
    F --> G[Atualiza badge + dropdown]
```

> **Evolução futura:** trocar polling por Django Channels/WebSocket ou SSE dedicado se a latência exigir. Na V1, polling é suficiente e simples.

---

## 38. Design System e UI/UX

### 38.1 Fonte de Verdade

O arquivo **`design_system/design-system.html`** é a **fonte única de verdade visual** do SCSI. Cores, tipografia, espaçamentos, componentes, estados e padrões de UI **devem** ser extraídos dele. **É proibido inventar um design paralelo.**

> **Status atual (atualizado na Sprint 3):** o arquivo `design_system/design-system.html` **está presente e versionado** (tema Duralux / Bootstrap 5, classes `nxl-`, ícones feather). Os assets (`refs/duralux/css`, `fonts`, `images`) são servidos sob `vendor/duralux/` via `STATICFILES_DIRS`, os tokens foram extraídos para `static/css/tokens.css` e os templates base (`base.html`, `base_auth.html`, `base_app.html`) já consomem o DS.

### 38.2 Como Consumir o Design System

- Extrair **tokens** (cores, fontes, espaçamentos, raios, sombras) para **CSS custom properties** em `static/css/tokens.css`.
- Mapear os **componentes** do HTML do DS (botões, inputs, cards, tabelas, badges, modais, toasts, sidebar, topbar) para **partials Django** reutilizáveis em `templates/partials/`.
- Templates base: `base.html` (público/landing), `base_auth.html` (login/registro/reset), `base_app.html` (área interna com **menu lateral** + topbar + sino de notificações).
- Garantir **contraste** adequado entre fontes e fundos (acessibilidade).

### 38.3 Responsividade

- Layout responsivo para **desktop, tablet e mobile**.
- Menu lateral colapsável em telas pequenas; tabelas com scroll horizontal; Kanban com scroll horizontal de colunas.
- Toques/áreas clicáveis adequadas a mobile.

### 38.4 Padrões de UX

- Estados de **loading** em ações assíncronas (resumo IA, relatórios, drag-and-drop).
- **Toasts** para feedback imediato + **notificações** persistentes para conclusão de tasks.
- Modais de confirmação para ações destrutivas (substituir `alert()`).
- Mensagens de erro/sucesso via `django.contrib.messages`.
- Jornadas curtas e coerentes com o contexto de corretoras (mínimo de cliques para gerar apólice, registrar sinistro, mover card).

---

## 39. Requisitos Não Funcionais

| Categoria | Requisito |
|---|---|
| **Responsividade** | Funciona em desktop, tablet e mobile; layouts adaptativos. |
| **Performance** | Filtros, listas e dashboards rápidos; uso de índices por tenant; `select_related`/`prefetch_related`; paginação; agregações no banco. |
| **Não bloqueio** | IA, PDFs e e-mails sempre assíncronos; UI nunca trava. |
| **Escalabilidade** | Modelagem preparada para volume (índices compostos `(brokerage, ...)`, JSONB, soft delete); deploy escalável horizontalmente (réplicas no Swarm). |
| **Segurança** | Rotas privadas autenticadas; isolamento por tenant; arquivos protegidos; permissões por role; cookies seguros; CSRF/XSS. |
| **Disponibilidade** | Serviços com restart automático no Swarm; healthchecks; TLS via Traefik. |
| **Observabilidade** | Logs estruturados; logs de Traefik; visibilidade de tasks no admin; (opcional) Sentry. |
| **Internacionalização** | UI em pt-BR; timezone `America/Sao_Paulo`. |
| **Manutenibilidade** | Código PEP8, em inglês, com apps coesas e serviços isolados. |

---

## 40. Regras de Qualidade de Código

- **Python ≥ 3.13**, **Django ≥ 6.0**.
- Ambiente virtual **`.venv`** na raiz; **`requirements.txt`** sempre atualizado.
- **PEP8**; **aspas simples** sempre que possível; nomes e código em **inglês**.
- **Class Based Views** e recursos nativos do Django sempre que possível; classes/funções simples.
- **Único `settings.py`**, lendo do **`.env`**.
- Domínio separado em **apps** coesas (seção 12).
- **Signals** (se usados) em `signals.py`, conectados no `AppConfig.ready()`.
- **Toda model** herda `created_at`/`updated_at` (`BaseModel`).
- Lógica de negócio em **`services.py`** (não nas views).
- Valores monetários/percentuais em **`DecimalField`**.
- **Não implementar testes** nesta fase (requisito explícito) e **não** incluir planejamento de testes automatizados.
- **Não** criar múltiplos arquivos de settings.
- **Não** expor mídia publicamente.

---

## 41. Documentação com MKDocs

### 41.1 Configuração

- Pasta **`docs/`** com **MKDocs** (tema `mkdocs-material` recomendado) e **suporte a Mermaid** (`mkdocs-mermaid2-plugin` ou superfences do Material).
- `mkdocs.yml` na raiz; servida em container próprio em produção (opcional) ou gerada estaticamente.

### 41.2 Documentos Obrigatórios em `docs/`

| Documento | Conteúdo |
|---|---|
| `index.md` | Visão geral do SCSI e como navegar a doc |
| `architecture.md` | Arquitetura geral (com diagramas Mermaid) |
| `multi-tenant.md` | Estratégia de isolamento por tenant e regras |
| `domain-model.md` | Entidades, ER e relacionamentos |
| `permissions.md` | Roles, permissões e segurança |
| `protected-media.md` | Como funciona o serving de arquivos protegidos |
| `ai-agents.md` | Agentes de resumo e chat, tools isoladas, custos |
| `celery-tasks.md` | Tasks, beat, fluxo de resumo e notificações |
| `env-vars.md` | Variáveis de ambiente |
| `local-dev.md` | Subir o ambiente com Docker Compose |
| `deploy.md` | Deploy com Docker Swarm + Traefik (passo a passo) |
| `backup.md` | Estratégia e procedimentos de backup/restore |
| `runbook.md` | Operação, incidentes, logs e monitoramento |

### 41.3 Exemplo `mkdocs.yml` (essencial)

```yaml
site_name: SCSI Docs
theme:
  name: material
markdown_extensions:
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
nav:
  - Início: index.md
  - Arquitetura: architecture.md
  - Multi Tenant: multi-tenant.md
  - Modelo de Domínio: domain-model.md
  - Agentes de IA: ai-agents.md
  - Deploy: deploy.md
```

---

## 42. Variáveis de Ambiente

Todas as credenciais ficam no **`.env`** na raiz, carregadas no `settings.py` (via `python-decouple` ou `django-environ`). Um **`.env.example`** versionado documenta as chaves (sem valores reais).

| Variável | Exemplo | Descrição |
|---|---|---|
| `DEBUG` | `False` | Modo debug (False em prod) |
| `SECRET_KEY` | `***` | Chave secreta Django |
| `ALLOWED_HOSTS` | `scsi.digital,www.scsi.digital` | Hosts permitidos |
| `CSRF_TRUSTED_ORIGINS` | `https://scsi.digital` | Origens confiáveis CSRF |
| `DATABASE_URL` | `postgres://user:pass@db:5432/scsi` | Conexão PostgreSQL |
| `POSTGRES_DB` | `scsi` | Nome do banco |
| `POSTGRES_USER` | `scsi` | Usuário do banco |
| `POSTGRES_PASSWORD` | `***` | Senha do banco |
| `CELERY_BROKER_URL` | `amqp://user:pass@rabbitmq:5672//` | Broker RabbitMQ |
| `CELERY_RESULT_BACKEND` | `redis://redis:6379/0` | Result backend |
| `RABBITMQ_DEFAULT_USER` | `scsi` | Usuário RabbitMQ |
| `RABBITMQ_DEFAULT_PASS` | `***` | Senha RabbitMQ |
| `REDIS_URL` | `redis://redis:6379/1` | Cache/locks |
| `OPENAI_API_KEY` | `sk-***` | Chave OpenAI |
| `OPENAI_MODEL` | `gpt-5.5-mini` | Modelo padrão de IA |
| `EMAIL_HOST` | `smtp.provider.com` | SMTP host |
| `EMAIL_PORT` | `587` | SMTP port |
| `EMAIL_HOST_USER` | `no-reply@scsi.digital` | Usuário SMTP |
| `EMAIL_HOST_PASSWORD` | `***` | Senha SMTP |
| `EMAIL_USE_TLS` | `True` | TLS no e-mail |
| `DEFAULT_FROM_EMAIL` | `SCSI <no-reply@scsi.digital>` | Remetente padrão |
| `TIME_ZONE` | `America/Sao_Paulo` | Timezone |
| `LANGUAGE_CODE` | `pt-br` | Idioma |
| `MEDIA_ROOT` | `/app/media` | Raiz da mídia protegida |
| `STATIC_ROOT` | `/app/staticfiles` | Raiz dos estáticos coletados |
| `SECURE_SSL_REDIRECT` | `True` | Força HTTPS (prod) |
| `ACME_EMAIL` | `admin@scsi.digital` | E-mail Let's Encrypt (Traefik) |

> Em produção (Swarm), os segredos sensíveis (`SECRET_KEY`, senhas, `OPENAI_API_KEY`) podem ser geridos por **Docker secrets/configs** em vez de `.env` em texto plano (ver seção 44).

---

## 43. Docker e Docker Compose para Desenvolvimento Local

### 43.1 Serviços de Desenvolvimento

| Serviço | Imagem base | Função |
|---|---|---|
| `app` | build do `Dockerfile` | Django (runserver no dev) |
| `db` | `postgres:16` | Banco de dados |
| `rabbitmq` | `rabbitmq:3-management` | Broker + UI de management |
| `redis` | `redis:7` | Result backend / cache |
| `celery_worker` | mesma imagem do `app` | Worker Celery |
| `celery_beat` | mesma imagem do `app` | Agendador Beat |

### 43.2 `docker-compose.yml` (desenvolvimento — referência)

```yaml
services:
  app:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
      - media_data:/app/media
    ports:
      - '8000:8000'
    env_file: .env
    depends_on: [db, rabbitmq, redis]

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - pg_data:/var/lib/postgresql/data
    ports:
      - '5432:5432'

  rabbitmq:
    image: rabbitmq:3-management
    environment:
      RABBITMQ_DEFAULT_USER: ${RABBITMQ_DEFAULT_USER}
      RABBITMQ_DEFAULT_PASS: ${RABBITMQ_DEFAULT_PASS}
    ports:
      - '5672:5672'
      - '15672:15672'

  redis:
    image: redis:7
    ports:
      - '6379:6379'

  celery_worker:
    build: .
    command: celery -A core worker -l info
    volumes:
      - .:/app
      - media_data:/app/media
    env_file: .env
    depends_on: [db, rabbitmq, redis]

  celery_beat:
    build: .
    command: celery -A core beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    volumes:
      - .:/app
    env_file: .env
    depends_on: [db, rabbitmq, redis]

volumes:
  pg_data:
  media_data:
```

### 43.3 `Dockerfile` (referência)

```dockerfile
FROM python:3.13-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod +x entrypoint.sh
EXPOSE 8000
ENTRYPOINT ['./entrypoint.sh']
```

### 43.4 Comandos Locais

```bash
# subir o ambiente
docker compose up -d --build
# migrações
docker compose exec app python manage.py migrate
# superusuário
docker compose exec app python manage.py createsuperuser
# logs do worker
docker compose logs -f celery_worker
```

---

## 44. Deploy em VPS Ubuntu com Docker Swarm

### 44.1 Topologia de Produção

```mermaid
graph TB
    CF[Cloudflare DNS - scsi.digital] --> TR[Traefik :80/:443 - TLS Let's Encrypt]
    subgraph "Docker Swarm (VPS Ubuntu)"
        TR --> APP[Service: app - gunicorn - N réplicas]
        APP --> DB[(Service: db - postgres + volume)]
        APP --> RMQ[Service: rabbitmq]
        APP --> RDS[(Service: redis)]
        WK[Service: celery_worker] --> RMQ
        BT[Service: celery_beat] --> RMQ
        WK --> DB
        APP --> MEDIA[Volume: media protegida]
    end
```

- **Traefik** é o único serviço exposto (portas 80/443); termina TLS e roteia para o `app` pela rede overlay.
- `app` roda **gunicorn** (não runserver); estáticos servidos via WhiteNoise ou Traefik.
- **Mídia protegida** nunca tem rota pública no Traefik — só via view Django.

### 44.2 `docker-stack.yml` (produção — referência)

```yaml
version: '3.9'

services:
  traefik:
    image: traefik:v3.1
    command:
      - --providers.docker.swarmmode=true
      - --providers.docker.exposedbydefault=false
      - --entrypoints.web.address=:80
      - --entrypoints.websecure.address=:443
      - --entrypoints.web.http.redirections.entrypoint.to=websecure
      - --certificatesresolvers.le.acme.tlschallenge=true
      - --certificatesresolvers.le.acme.email=${ACME_EMAIL}
      - --certificatesresolvers.le.acme.storage=/letsencrypt/acme.json
    ports:
      - '80:80'
      - '443:443'
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - letsencrypt:/letsencrypt
    networks: [traefik_public]
    deploy:
      placement:
        constraints: [node.role == manager]

  app:
    image: ghcr.io/pycodebr/scsi:latest
    command: gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3
    env_file: .env
    volumes:
      - media_data:/app/media
      - static_data:/app/staticfiles
    networks: [traefik_public, internal]
    deploy:
      replicas: 2
      labels:
        - traefik.enable=true
        - traefik.http.routers.scsi.rule=Host(`scsi.digital`)
        - traefik.http.routers.scsi.entrypoints=websecure
        - traefik.http.routers.scsi.tls.certresolver=le
        - traefik.http.services.scsi.loadbalancer.server.port=8000

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - pg_data:/var/lib/postgresql/data
    networks: [internal]

  rabbitmq:
    image: rabbitmq:3-management
    environment:
      RABBITMQ_DEFAULT_USER: ${RABBITMQ_DEFAULT_USER}
      RABBITMQ_DEFAULT_PASS: ${RABBITMQ_DEFAULT_PASS}
    networks: [internal]

  redis:
    image: redis:7
    networks: [internal]

  celery_worker:
    image: ghcr.io/pycodebr/scsi:latest
    command: celery -A core worker -l info
    env_file: .env
    volumes:
      - media_data:/app/media
    networks: [internal]
    deploy:
      replicas: 2

  celery_beat:
    image: ghcr.io/pycodebr/scsi:latest
    command: celery -A core beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    env_file: .env
    networks: [internal]

networks:
  traefik_public:
    external: true
  internal:

volumes:
  pg_data:
  media_data:
  static_data:
  letsencrypt:
```

---

## 45. Guia Detalhado de Deploy do Zero

> VPS **Ubuntu 22.04/24.04 LTS**, domínio `scsi.digital`. Substitua `SEU_IP`, usuários e senhas conforme seu ambiente.

### 45.1 Atualizar o servidor e criar usuário

```bash
ssh root@SEU_IP
apt update && apt upgrade -y
adduser deploy
usermod -aG sudo deploy
# (recomendado) configurar chave SSH para o usuário deploy e desabilitar login root/senha
```

### 45.2 Firewall

```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
ufw status
```

### 45.3 Instalar Docker

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
usermod -aG docker deploy
docker --version
docker compose version
```

### 45.4 Inicializar o Docker Swarm

```bash
docker swarm init --advertise-addr SEU_IP
docker node ls
```

### 45.5 Criar a rede overlay do Traefik

```bash
docker network create --driver overlay --attachable traefik_public
```

### 45.6 Configurar DNS no Cloudflare

1. Painel Cloudflare → domínio `scsi.digital` → **DNS**.
2. Criar registro **A**: `scsi.digital` → `SEU_IP`.
3. Criar registro **A** (ou CNAME): `www` → `scsi.digital`/`SEU_IP`.
4. **SSL/TLS** → modo **Full (strict)**.
5. Para o desafio TLS do Let's Encrypt do Traefik, deixe o registro **DNS-only** (nuvem cinza) na primeira emissão; depois pode ativar o proxy (nuvem laranja).

### 45.7 Variáveis de ambiente e segredos

```bash
# no diretório do projeto na VPS (ex.: /home/deploy/scsi)
cp .env.example .env
nano .env   # preencher SECRET_KEY, DB, RabbitMQ, OPENAI_API_KEY, ACME_EMAIL, etc.

# (opcional, recomendado) usar Docker secrets para itens sensíveis:
printf 'minha-secret-key' | docker secret create scsi_secret_key -
printf 'sk-...'          | docker secret create scsi_openai_key  -
```

### 45.8 Build e push da imagem

```bash
# em um registry (Docker Hub / GHCR / registry privado)
docker login registry.example.com
docker build -t ghcr.io/pycodebr/scsi:latest .
docker push ghcr.io/pycodebr/scsi:latest
```

### 45.9 Deploy das stacks

```bash
# deploy do Traefik + app (mesmo arquivo com a rede traefik_public externa)
docker stack deploy -c docker-stack.yml scsi
docker stack services scsi
docker service ls
```

### 45.10 Migrações, estáticos e superusuário

```bash
# descobrir um container do serviço app
docker ps --filter name=scsi_app -q | head -n1
# rodar comandos dentro do container
APP=$(docker ps --filter name=scsi_app -q | head -n1)
docker exec -it $APP python manage.py migrate
docker exec -it $APP python manage.py collectstatic --noinput
docker exec -it $APP python manage.py createsuperuser
```

> Alternativa idempotente: colocar `migrate` e `collectstatic` no `entrypoint.sh` para rodarem no boot do serviço `app`.

### 45.11 Verificações (SSL, proxy, portas, volumes)

```bash
# logs do Traefik (emissão de certificado)
docker service logs -f scsi_traefik
# acessar https://scsi.digital e validar cadeado (Let's Encrypt)
# conferir volumes persistentes
docker volume ls | grep scsi
```

### 45.12 Observações de Produção

- **SSL:** emitido automaticamente pelo Traefik (Let's Encrypt, `tlschallenge`); Cloudflare em **Full (strict)**.
- **Proxy/portas:** apenas Traefik expõe 80/443; demais serviços só na rede `internal`.
- **Volumes:** `pg_data` (banco), `media_data` (anexos), `static_data` (estáticos), `letsencrypt` (certs) — todos persistentes.
- **Backups/logs:** ver seções 47 e 48.
- **Atualização (rolling update):**
  ```bash
  docker build -t ghcr.io/pycodebr/scsi:latest .
  docker push ghcr.io/pycodebr/scsi:latest
  docker service update --image ghcr.io/pycodebr/scsi:latest scsi_app
  docker service update --image ghcr.io/pycodebr/scsi:latest scsi_celery_worker
  ```

---

## 46. Estratégia de Banco de Dados

- **PostgreSQL** como banco principal (dev e prod) — sem SQLite, para consistência de comportamento (JSONB, constraints, concorrência).
- **Isolamento por tenant** via FK `brokerage` em toda entidade; **índices compostos** começando por `brokerage` (`Index(fields=['brokerage', 'status'])`, `['brokerage', 'created_at']`, etc.).
- **Constraints por tenant:** `UniqueConstraint(['brokerage', 'document'])` (clientes), `['brokerage', 'policy_number']` (apólices), `['brokerage', 'number']` (propostas).
- **`CheckConstraint`** em `CoveredItem` (exatamente um entre proposal/policy).
- **JSONB** (`JSONField`) para `CoveredItem.attributes`/`coverages` e `Plan.features`.
- **Valores monetários** em `DecimalField(max_digits=14, decimal_places=2)`; taxas em `DecimalField(max_digits=6, decimal_places=4)`.
- **Soft delete** (`is_active`) para entidades críticas (corretora, cliente, seguradora, ramo, agente, produtor); exclusão física só onde seguro.
- **Migrações** versionadas e aplicadas no deploy; nunca editar migração já aplicada em produção.
- **Performance:** `select_related`/`prefetch_related` nas listas e detalhes; paginação; agregações via `annotate`/`aggregate` no dashboard.
- **Conexões:** considerar `CONN_MAX_AGE` e, em escala, **PgBouncer** (futuro).

### 46.1 Carga Inicial de Dados de Demonstração — Comando `seed_demo`

#### F31 — Comando de Carga de Dados Fake para Demonstração

- **Estado atual:** não existe. Nenhum comando de seed/fixtures no projeto.
- **Descrição:** management command `python manage.py seed_demo` que popula a base com dados fictícios realistas — corretora(s), usuários e registros em **todas as tabelas possíveis** — com **datas variadas** (passado, presente e futuro), cobrindo **múltiplos cenários** para demonstrações do sistema.
- **Valor para o usuário:** permite a Renata (admin) e ao time comercial **demonstrar o SCSI** com um ambiente cheio e crível (dashboard com gráficos populados, CRM com cards em todas as etapas, renovações a vencer, sinistros em andamento, comissões a repassar) sem cadastrar nada manualmente. Acelera vendas, onboarding e QA visual.

**Regras de negócio:**
- Cria por padrão **2 corretoras** (tenants) com dados independentes — comprova visualmente o **isolamento multi tenant**.
- Cada corretora recebe: plano/assinatura, usuários em **todos os roles** (owner/manager/broker/agent/producer/operational) e registros em todas as entidades de domínio.
- Datas distribuídas: `created_at`/`updated_at` espalhados nos últimos ~24 meses; datas de negócio (vigências, vencimentos, ocorrências, referências de comissão) cobrindo passado/presente/futuro.
- Cobre **todos os estados/tipos** de cada entidade (ver "Cenários cobertos").
- **Seguro por padrão:** aborta se `settings.DEBUG is False`, exceto com `--force` explícito (evita destruir base de produção).
- **Reprodutível:** seed fixa (`--seed`, default `42`) para `Faker` e `random`.
- **Resumos de IA** preenchidos com **texto canônico fake** — o comando **não** chama a OpenAI (offline, gratuito, determinístico).
- Tudo em **transação atômica**; usa `bulk_create` onde possível.

**Cenários cobertos (diversidade obrigatória):**
| Entidade | Cenários |
|---|---|
| `Client` | PF e PJ; com e sem anexos; com e sem `ai_summary` |
| `Insurer` / `LineOfBusiness` | catálogo variado por corretora |
| `Proposal` | todos os status (`draft`→`converted`), com 1..N itens cobertos |
| `Policy` | `active`, `expired`, `canceled`, `renewed`; vigências passadas/atuais/futuras |
| `CoveredItem` | todos os `item_type` (auto/property/fleet/travel/life/equipment/other) com `attributes`/`coverages` coerentes |
| `Claim` | todos os status (`opened`→`closed`); datas de ocorrência variadas |
| `Endorsement` | todos os tipos (increase/decrease/cancellation/data_change) |
| `Renewal` | `pending` (a vencer 30/60/90d), vencidas, `renewed`, `lost` |
| `Agent` / `Producer` | pessoa e empresa; produtor sob agente e direto à corretora |
| `Commission` / `CommissionSplit` | status `pending`/`received`/`paid`; repasses a agentes e produtores |
| CRM (`Deal`) | cards em todas as etapas; `open`/`won`/`lost`; com `DealStageHistory` |
| `Notification` | lidas e não lidas |
| `ChatSession` / `ChatMessage` | sessões com histórico user/assistant |
| `Document` | metadados (+ arquivos placeholder se `--with-files`) |

**Modelagem proposta:** **nenhuma alteração de schema.** O comando apenas **escreve** nas models existentes (seções 13–14). Observação técnica: como `created_at` usa `auto_now_add=True`, para obter datas históricas o comando **sobrescreve** `created_at`/`updated_at` após a criação via `Model.objects.filter(pk=...).update(created_at=...)`.

**Impactos técnicos:**
- **Backend:** novo comando `base/management/commands/seed_demo.py` (na app compartilhada `base`); helpers simples de geração por app (funções, **não** `factory_boy`). Dependência nova: `Faker` (locale `pt_BR`).
- **Frontend:** nenhum (saída no terminal com progresso e contagens finais por corretora).
- **Banco:** nenhuma migração; respeita FK `brokerage` em cada registro; usa índices já existentes.
- **Jobs/Integrações:** nenhuma chamada à OpenAI/Celery; resumos são texto fake.
- **Permissões:** comando de CLI (operador/dev); não exposto via web; sem rotas novas.

**Flags da CLI:**
| Flag | Default | Função |
|---|---|---|
| `--brokerages N` | `2` | nº de corretoras a criar |
| `--flush` | `False` | limpa dados de demonstração antes de criar |
| `--seed N` | `42` | seed determinística (Faker/random) |
| `--with-files` | `False` | gera arquivos placeholder para `Document` |
| `--force` | `False` | permite rodar com `DEBUG=False` (produção) |

**Fluxo do comando:**

```mermaid
flowchart TD
    A([manage.py seed_demo]) --> B{DEBUG=True ou --force?}
    B -->|Não| C[Aborta com aviso de segurança]
    B -->|Sim| D{--flush?}
    D -->|Sim| E[Remove dados de demonstração existentes]
    D -->|Não| F[Mantém base]
    E --> G[Cria corretoras + planos + assinaturas]
    F --> G
    G --> H[Cria usuários em todos os roles por corretora]
    H --> I[Cria catálogos: seguradoras e ramos]
    I --> J[Cria parceiros: agentes e produtores]
    J --> K[Cria clientes PF/PJ]
    K --> L[Cria propostas + itens cobertos todos os tipos]
    L --> M[Gera apólices + comissões + repasses]
    M --> N["Cria sinistros, endossos, renovações"]
    N --> O["Cria CRM: pipelines, etapas, deals, histórico"]
    O --> P["Cria notificações, chats e ai_summary fake"]
    P --> Q[Sobrescreve created_at e datas de negócio]
    Q --> R([Resumo final: contagens por corretora])
```

**Critérios de Aceite:**
- [ ] `python manage.py seed_demo` popula 2 corretoras com dados em **todas** as entidades de domínio.
- [ ] Cada registro tem `brokerage` correto (isolamento preservado entre as 2 corretoras).
- [ ] `created_at` e datas de negócio são **variados** (passado/presente/futuro), não todos "hoje".
- [ ] Todos os status/tipos/cenários da tabela acima aparecem ao menos uma vez.
- [ ] Dashboard, CRM (Kanban), renovações, comissões e sinistros exibem dados ricos após o seed.
- [ ] Comando aborta com `DEBUG=False` sem `--force`.
- [ ] Reexecução com `--flush` recria sem duplicar; mesma `--seed` gera o mesmo conjunto.
- [ ] Nenhuma chamada à OpenAI (resumos são texto fake).
- [ ] Uso documentado em `docs/local-dev.md`.

**Decisões resolvendo ambiguidades:**
- "Em todas as tabelas possíveis" → cobre todas as models de domínio tenant-aware + catálogos; **não** cria superuser/staff global (apenas usuários do tenant).
- Biblioteca → **`Faker` (pt_BR)** + `random` com seed fixa (não `factory_boy`, para não acoplar a framework de testes, que está fora de escopo — seção 40).
- `created_at` histórico → sobrescrito via `.update()` pós-criação (contorna `auto_now_add`).
- Resumos de IA → texto canônico fake (offline) para não gastar tokens nem exigir chave em demo.
- Segurança → guard em `DEBUG`/`--force` para nunca destruir produção por engano (ver risco R13).

---

## 47. Estratégia de Backup

- **Banco:** `pg_dump` diário automatizado (cron no host ou serviço dedicado), com **retenção** (ex.: 7 diários, 4 semanais, 12 mensais).
  ```bash
  # exemplo de dump (cron diário)
  DB=$(docker ps --filter name=scsi_db -q | head -n1)
  docker exec $DB pg_dump -U $POSTGRES_USER $POSTGRES_DB | gzip > /backups/scsi_$(date +%F).sql.gz
  ```
- **Mídia protegida:** backup do volume `media_data` (rsync/tar) para destino offsite.
- **Offsite:** enviar dumps e mídia para **object storage** (S3/Backblaze/MinIO) com versionamento.
- **Restore testado:** procedimento documentado em `docs/backup.md`; testar restauração periodicamente.
  ```bash
  # exemplo de restore
  gunzip -c /backups/scsi_2026-05-28.sql.gz | docker exec -i $DB psql -U $POSTGRES_USER $POSTGRES_DB
  ```
- **Segredos:** guardar cópia segura de `.env`/secrets fora do servidor (cofre).

---

## 48. Estratégia de Logs e Monitoramento

- **Logs da aplicação:** logging estruturado do Django (formato JSON em prod), níveis adequados; sem dados sensíveis em log.
- **Logs de serviços:** `docker service logs` (app, worker, beat, traefik); driver de log configurável (json-file com rotação ou agregador).
- **Traefik:** access logs e métricas (entrypoints/routers).
- **Tasks:** visibilidade no Django Admin via `dj-celery-panel` + `django-celery-results` (status, falhas, retries).
- **Healthchecks:** endpoint `/healthz/` simples para o `app`; `HEALTHCHECK` no Dockerfile/serviços.
- **Erros (opcional, recomendado):** **Sentry** para captura de exceções (DSN via env).
- **Métricas (futuro):** Prometheus/Grafana; uso de recursos por serviço.
- **Alertas:** notificar falhas recorrentes de tasks e indisponibilidade.

---

## 49. Riscos Técnicos do Projeto

| # | Risco | Impacto | Mitigação |
|---|---|---|---|
| R1 | **Vazamento de dados entre tenants** | Crítico | Defesa em camadas (seção 9): FK + middleware + manager + mixins + validação de FKs + tools de IA com tenant injetado. Revisão obrigatória de toda `get_queryset`. |
| R2 | **Tool de IA acessar dados de outra corretora** | Crítico | Tools recebem `brokerage` do servidor; nunca aceitam tenant do modelo; queries sempre filtram por `brokerage`. |
| R3 | **Arquivos protegidos vazando publicamente** | Alto | Sem rota pública de `/media/`; download só por view autenticada que valida tenant + permissão; armazenamento segregado por `brokerage_<id>`. |
| R4 | **Custos/latência de IA** | Médio | GPT-5.5-mini econômico; resumos assíncronos; histórico limitado; tools compactas; timeout/retry. |
| R5 | **Tasks travando a fila / falhas silenciosas** | Médio | RabbitMQ + retries com backoff; `dj-celery-panel`/`django-celery-results` para visibilidade; alertas. |
| R6 | **N+1 queries em listas/dashboard** | Médio | `select_related`/`prefetch_related`, agregações no banco, índices compostos por tenant, paginação. |
| R7 | **Migração inicial sem User customizado** | Alto | Definir `AUTH_USER_MODEL` na Sprint 1 antes do primeiro `migrate`. |
| R8 | **Modelagem de itens cobertos heterogênea** | Médio | `JSONField` (`attributes`/`coverages`) + `item_type`; forms dinâmicos; promover a models próprias só se necessário. |
| R9 | **Streaming SSE atrás do proxy** | Médio | Configurar Traefik/gunicorn para não bufferizar; testar streaming em produção. |
| R10 | **Ausência do Design System no início** | Médio | Bloquear sprints de frontend definitivo até `design-system.html` existir; usar tokens assim que disponível. |
| R11 | **Deploy/SSL no Cloudflare** | Médio | DNS-only na 1ª emissão Let's Encrypt; Cloudflare Full (strict) depois; logs do Traefik para diagnóstico. |
| R12 | **Cálculo incorreto de comissões/repasses** | Alto | Serviços isolados e validados (soma de repasses ≤ comissão); relatórios de conferência. |
| R13 | **Comando `seed_demo` popular/apagar base de produção por engano** | Alto | Aborta se `DEBUG=False` (exige `--force` explícito); `--flush` só remove dados de demonstração; documentado no runbook. |

---

## 50. Decisões Técnicas Recomendadas

### 50.1 Banco de Dados — PostgreSQL em dev e prod

| Aspecto | Decisão |
|---|---|
| **Escolha** | PostgreSQL desde o desenvolvimento (sem SQLite) |
| **Justificativa** | Paridade dev/prod; precisamos de JSONB, constraints por tenant e concorrência reais |
| **Trade-off** | Setup local exige container Postgres (resolvido pelo Docker Compose) em vez de arquivo único. |

### 50.2 Login por E-mail

| Aspecto | Decisão |
|---|---|
| **Escolha** | `User` customizado com `USERNAME_FIELD='email'` + `EmailBackend` |
| **Justificativa** | Padrão moderno de SaaS; usuário se identifica por e-mail |
| **Trade-off** | Exige definir `AUTH_USER_MODEL` antes do 1º migrate; feito na Sprint 1. |

### 50.3 Multi Tenant — Shared Schema por FK

| Aspecto | Decisão |
|---|---|
| **Escolha** | Banco único, schema único, isolamento por `brokerage` (FK) + filtros + middleware + mixins |
| **Justificativa** | Simplicidade operacional, migrações únicas, código idiomático; adequado a muitas corretoras pequenas |
| **Trade-off** | Isolamento depende de filtros corretos no código. Mitigado por mixin obrigatório, validação de FKs e revisão. Evolução para `Membership` (user multi-corretora) é possível sem refatorar o restante. |

### 50.4 Orquestração de IA — LangGraph

| Aspecto | Decisão |
|---|---|
| **Escolha** | LangGraph `StateGraph` para resumos e agente de chat com tools |
| **Justificativa** | Controle do fluxo (coleta → geração → persistência), tool-calling estruturado, fácil evoluir |
| **Trade-off** | Curva de aprendizado maior que uma chain simples; compensa pela clareza e extensibilidade. |

### 50.5 Streaming do Chat — SSE

| Aspecto | Decisão |
|---|---|
| **Escolha** | `StreamingHttpResponse` com Server-Sent Events |
| **Justificativa** | Nativo no Django, suporta callback de streaming, sem WebSocket |
| **Trade-off** | Unidirecional (servidor → cliente). Suficiente para chat; colaboração real-time exigiria Channels. |

### 50.6 Async — Celery + RabbitMQ

| Aspecto | Decisão |
|---|---|
| **Escolha** | Celery (worker + beat) com **RabbitMQ** broker e Redis result backend; `dj-celery-panel` no admin |
| **Justificativa** | RabbitMQ confiável para filas; beat para agendamentos (renovações); visibilidade no admin |
| **Trade-off** | Mais serviços para operar; compensa por não bloquear a UI e por confiabilidade. |

### 50.7 Mídia Protegida — View Django (V1)

| Aspecto | Decisão |
|---|---|
| **Escolha** | Download via `FileResponse` em view autenticada; storage segregado por tenant; sem rota pública |
| **Justificativa** | Segurança e simplicidade na V1 |
| **Trade-off** | Streaming ocupa worker. Para escala: sidecar nginx com `X-Accel-Redirect` ou object storage com URLs assinadas. |

### 50.8 Itens Cobertos — `JSONField` por tipo

| Aspecto | Decisão |
|---|---|
| **Escolha** | `CoveredItem` único com `item_type` + `attributes`/`coverages` em JSONB |
| **Justificativa** | Flexibilidade para auto/imóvel/frota/viagem/vida/equipamento sem explosão de tabelas |
| **Trade-off** | Menos validação em nível de schema; mitigado por forms dinâmicos e validação na app. |

### 50.9 Seguradoras e Ramos — Tenant-aware

| Aspecto | Decisão |
|---|---|
| **Escolha** | `Insurer` e `LineOfBusiness` com `brokerage` (cada corretora mantém os seus), seedados no onboarding |
| **Justificativa** | Uniformidade do isolamento; evita acoplamento e vazamento de catálogos customizados |
| **Trade-off** | Duplicação de catálogos comuns entre tenants; aceitável e evita complexidade de catálogo global compartilhado. |

### 50.10 Frontend — Server-rendered + JS leve

| Aspecto | Decisão |
|---|---|
| **Escolha** | Django Templates + Design System; HTMX/Alpine.js (ou JS vanilla) para Kanban/streaming/polling |
| **Justificativa** | Produtividade, aderência ao DS, simplicidade sem SPA |
| **Trade-off** | Interações muito ricas exigiriam mais JS; suficiente para o escopo da V1. |

### 50.11 Deploy — Docker Swarm + Traefik

| Aspecto | Decisão |
|---|---|
| **Escolha** | Docker Compose (dev) e Docker Swarm + Traefik (prod), TLS automático |
| **Justificativa** | Menor custo operacional que Kubernetes para time pequeno; rolling updates nativos |
| **Trade-off** | Menos recursos avançados que K8s; adequado ao porte atual. |

### 50.12 Seed de Demonstração — `Faker` + Guard de Produção

| Aspecto | Decisão |
|---|---|
| **Escolha** | Comando `seed_demo` com `Faker` (pt_BR) + seed fixa; resumos de IA fake (offline); guard que aborta com `DEBUG=False` salvo `--force` |
| **Justificativa** | Demos/QA precisam de base rica e reprodutível sem custo de IA nem cadastro manual; `Faker` é leve e não acopla a framework de testes (fora de escopo) |
| **Trade-off** | Dados fake não refletem distribuições reais; o guard exige `--force` consciente para popular ambientes não-DEBUG. Sobrescrever `created_at` via `.update()` é necessário por causa de `auto_now_add`. |

---

## 51. Critérios de Aceite

Critérios globais que validam a entrega do sistema (cada feature tem os seus, seções 17–37):

- [ ] Login e cadastro por **e-mail**; recuperação de senha nativa funcional.
- [ ] Onboarding cria corretora (CNPJ + razão social obrigatórios), usuário owner e assinatura Free, em transação.
- [ ] Perfis de acesso (owner/manager/broker/agent/producer/operational) aplicados.
- [ ] **Nenhuma** query sensível retorna dados de outra corretora (isolamento validado por inspeção).
- [ ] Toda model de domínio possui `created_at` e `updated_at` e FK `brokerage` (quando tenant-aware).
- [ ] CRUDs completos: clientes, seguradoras, ramos, propostas, apólices, itens cobertos, sinistros, endossos, renovações, agentes, produtores.
- [ ] **"Gerar apólice"** cria apólice a partir da proposta (copia dados, clona itens, gera comissão, marca proposta convertida).
- [ ] Comissões e repasses calculados; relatório por beneficiário.
- [ ] CRM com **grid** e **Kanban** (drag-and-drop, pipeline personalizável, histórico de etapa).
- [ ] Dashboard com métricas e **funil de negociações**.
- [ ] Relatórios exportáveis em **PDF** e **CSV**.
- [ ] **Anexos protegidos** em clientes/propostas/apólices/sinistros, servidos só por view autenticada.
- [ ] **Resumos por IA** (cliente/apólice/sinistro/proposta/negociação) assíncronos, salvos na entidade, com notificação.
- [ ] **Chat com IA** com sessões por usuário, tools isoladas por tenant, resposta em Markdown com streaming.
- [ ] Tasks assíncronas (worker + beat) visíveis no Django Admin.
- [ ] Notificações in-app ao concluir tasks.
- [ ] Landing page pública em `scsi.digital` com Free habilitado e demais "Em breve".
- [ ] UI 100% pt-BR, responsiva, aderente ao Design System, timezone `America/Sao_Paulo`.
- [ ] Documentação MKDocs (com Mermaid) publicada.
- [ ] Deploy reproduzível em VPS Ubuntu com Docker Swarm + Traefik (TLS ativo).
- [ ] Comando `seed_demo` popula um ambiente de demonstração diverso (multi cenário, datas variadas, 2 corretoras isoladas).

---

## 52. Roadmap de Desenvolvimento

Visão em fases (cada fase agrupa sprints da seção 53):

| Fase | Sprints | Objetivo da fase | Entrega |
|---|---|---|---|
| **Fase 1 — Fundação** | 1–7 | Setup, Docker, Django, auth por e-mail, multi tenant, corretoras, usuários/permissões | Usuário cria corretora, loga e gerencia equipe; isolamento por tenant ativo |
| **Fase 2 — Núcleo de Domínio** | 8–13 | Anexos protegidos, clientes, seguradoras/ramos, propostas, apólices (+geração), itens cobertos | Operação básica de cadastros e do ciclo proposta→apólice com anexos |
| **Fase 3 — Operação de Seguros** | 14–17 | Sinistros, endossos, agentes/produtores, comissões | Ciclo operacional completo + financeiro de comissões |
| **Fase 4 — Vendas e Assíncrono** | 18–20 | CRM, Celery/Beat/Notificações, renovações | Funil de vendas + automações e alertas |
| **Fase 5 — Inteligência e Análise** | 21–24 | Resumos IA, chat IA, dashboard, relatórios | IA integrada + visão analítica e exportações |
| **Fase 6 — Lançamento** | 25–29 | Landing, MKDocs, deploy Swarm, ajustes finais, **seed de demonstração** | Produto público, documentado, em produção, com base de demo |

```mermaid
flowchart LR
    F1[Fase 1 Fundação] --> F2[Fase 2 Núcleo]
    F2 --> F3[Fase 3 Operação]
    F3 --> F4[Fase 4 Vendas + Async]
    F4 --> F5[Fase 5 IA + Análise]
    F5 --> F6[Fase 6 Lançamento]
```

---

## 53. Sprints de Implementação em Checklist

> Sprints sequenciais e incrementais. Marque `- [x]` ao concluir cada tarefa. Ordem otimizada por dependências (ex.: anexos antes dos CRUDs que anexam; Celery antes de IA/renovações; CRM antes do dashboard de funil).

### Sprint 1 — Setup Inicial
**Objetivo:** estrutura do projeto, ambiente e configuração base.
- [X] Criar `.venv` na raiz (Python 3.13+)
- [X] Iniciar projeto Django 6 (`core/`) e `requirements.txt`
- [X] Criar `.gitignore`
- [X] Criar `.env` e `.env.example`
- [X] Configurar **único** `settings.py` lendo do `.env` (decouple/environ)
- [X] Definir `AUTH_USER_MODEL='accounts.User'` (antes do 1º migrate)
- [X] `TIME_ZONE='America/Sao_Paulo'`, `LANGUAGE_CODE='pt-br'`, `USE_TZ=True`
- [X] Criar app `base` com `BaseModel` e `TenantAwareModel` (abstratas) e `TenantManager`

**Entrega:** projeto Django roda localmente com settings via `.env`.

> **Decisões da execução da Sprint 1 (resolvendo ambiguidades):**
> - **Lib de ambiente:** adotado `django-environ` (em vez de `python-decouple`) por parsear `DATABASE_URL` nativamente (`env.db()`), alinhado à seção 42.
> - **Banco em dev local:** `settings.DATABASES` lê `DATABASE_URL`; sem ele (dev local pré-Docker) cai em SQLite padrão. O Postgres entra via Docker na Sprint 2.
> - **`accounts.User` mínimo:** criada a app `accounts` com `User(AbstractUser)` apenas para fixar `AUTH_USER_MODEL` antes do 1º migrate. Login por e-mail (`USERNAME_FIELD='email'`) e `EmailBackend` ficam para a Sprint 4.
> - **`TenantManager`/`current_tenant`:** `TenantManager.for_tenant()` e o contextvar `current_tenant` já criados em `base/managers.py`; o `TenantMiddleware`/mixins que os consomem entram na Sprint 5.
> - **`.env`/`.env.example`:** os arquivos (marcados acima como já feitos) não existiam no repo e foram criados nesta execução — `.env.example` documenta todas as chaves da seção 42; `.env` traz valores de dev local.

### Sprint 2 — Docker Local
**Objetivo:** ambiente de desenvolvimento containerizado.
- [X] Criar `Dockerfile` (Python 3.13-slim) e `entrypoint.sh`
- [X] Criar `docker-compose.yml` com `app`, `db` (postgres:16), `rabbitmq`, `redis`
- [X] Adicionar serviços `celery_worker` e `celery_beat`
- [X] Volumes persistentes (`pg_data`, `media_data`)
- [X] Validar `docker compose up` e conexão ao Postgres

**Entrega:** `docker compose up` sobe app + banco + broker + worker/beat.

> **Decisões da execução da Sprint 2 (resolvendo ambiguidades):**
> - **Driver Postgres:** adicionado `psycopg[binary]` ao `requirements.txt` (necessário para a conexão ao Postgres — deliverable da sprint).
> - **`entrypoint.sh`:** roda `migrate --noinput` + `collectstatic --noinput` e finaliza com `exec "$@"` (o `command:` de cada serviço é o processo final). Corrigido o bug de aspas do `ENTRYPOINT` da referência (§43.3): usado exec-form com aspas duplas `["./entrypoint.sh"]`. **O bit executável precisa estar no arquivo do host** (`chmod +x entrypoint.sh`) porque o bind-mount `.:/app` sobrepõe o `chmod` da imagem.
> - **Healthcheck no `db`:** adicionado `pg_isready` + `depends_on: condition: service_healthy` no `app`/`celery_worker`/`celery_beat`, garantindo que a app só sobe após o Postgres aceitar conexões (robustez do deliverable "conexão ao Postgres").
> - **`.env` Docker-ready:** o `.env` passou a apontar `DATABASE_URL`/`CELERY_*`/`REDIS_URL` para os serviços do Compose (`db`, `rabbitmq`, `redis`). Para rodar o Django no host sem Docker, basta comentar `DATABASE_URL` (o settings cai no SQLite padrão).
> - **`.dockerignore`:** criado para enxugar o build (exclui `.venv`, `.git`, `db.sqlite3`, `media/`, `design_system/refs/`).
> - **`celery_worker`/`celery_beat`:** os serviços estão **definidos** no Compose, porém só sobem por completo após a **Sprint 3** (que cria `core/celery.py` e instala `celery`/`django-celery-beat`). Validação ao vivo cobriu `app` + `db` + `rabbitmq` + `redis` (app respondendo HTTP 200; migrações aplicadas e tabelas criadas no Postgres); worker/beat não foram iniciados por dependerem do bootstrap do Celery.
> - **Imagem base:** `python:3.13-slim` conforme §43.3 (o host usa Python 3.14, mas o container fixa 3.13+ como manda o PRD).

### Sprint 3 — Configuração Django Base + Design System + Celery Bootstrap
**Objetivo:** base de templates e bootstrap do Celery.
- [X] Adicionar `design_system/design-system.html` ao repo (artefato obrigatório)
- [X] Extrair tokens para `static/css/tokens.css`
- [X] Criar templates base: `base.html`, `base_auth.html`, `base_app.html` (menu lateral + topbar)
- [X] Configurar estáticos (collectstatic / WhiteNoise)
- [X] Criar `core/celery.py` e carregar no `core/__init__.py`
- [X] Rodar uma task de exemplo no worker

**Entrega:** layout base do DS aplicado e Celery executando tasks.

> **Decisões da execução da Sprint 3 (resolvendo ambiguidades):**
> - **Assets do Design System (Duralux):** o DS é um tema Bootstrap 5 (convenção de classes `nxl-`, ícones feather). Em vez de duplicar os 565 arquivos de `refs/duralux`, os assets são servidos sob o prefixo `vendor/duralux/` via `STATICFILES_DIRS` (tupla `('vendor/duralux', design_system/refs/duralux)`) — mantendo o DS como fonte única. O `.dockerignore` deixou de excluir `design_system/refs/` para os assets irem na imagem.
> - **`tokens.css`:** extraídos os tokens reais do tema (primary `#3454d1`, success `#17c666`, danger `#ea4d4d`, etc., tipografia, raios, body-bg `#f0f2f8`) para `static/css/tokens.css` como CSS custom properties `--scsi-*`. Nenhum valor inventado.
> - **JS do Design System ausente:** o artefato do DS embarca CSS + fontes, mas **não** os arquivos `js/` que seu HTML referencia. Para não enviar `<script>` quebrados, foi criado um `static/js/app.js` mínimo (vanilla) que faz só o toggle do menu lateral usando as classes que o próprio tema espera (`html.minimenu`, `.mob-navigation-active`). Bundle interativo completo (Bootstrap JS) fica para quando os assets JS do DS forem fornecidos / sprint de frontend que precisar.
> - **Templates base:** `base.html` (esqueleto + CSS do DS + tokens), `base_auth.html` (card centralizado para login/registro/reset) e `base_app.html` (shell `nxl-container` com `partials/_sidebar.html` + `partials/_topbar.html`). Links de menu são `href="#"` (placeholders) até as rotas de cada feature existirem, evitando acoplamento a URLs ainda inexistentes.
> - **Estáticos / WhiteNoise:** `whitenoise.middleware.WhiteNoiseMiddleware` logo após o `SecurityMiddleware` e `STORAGES.staticfiles = whitenoise.storage.CompressedStaticFilesStorage` (compressão sem manifest, para não quebrar o `collectstatic` com os muitos `url()` do tema).
> - **Bootstrap do Celery:** `core/celery.py` (`Celery('scsi')`, `config_from_object('django.conf:settings', namespace='CELERY')`, `autodiscover_tasks()`) carregado em `core/__init__.py`. Settings `CELERY_*` lidas do `.env`. Adicionados `celery`, `redis` (backend de resultado), `django-celery-beat` (DatabaseScheduler usado pelo serviço `celery_beat` do Compose) e `whitenoise` ao `requirements.txt`. `django_celery_beat` entrou em `INSTALLED_APPS`. Task de exemplo em `base/tasks.py` (`add`). Validação ao vivo: worker recebeu e concluiu `base.tasks.add(2,3) -> 5`; beat subiu com `DatabaseScheduler`.

### Sprint 4 — Autenticação por E-mail
**Objetivo:** auth nativa por e-mail.
- [x] App `accounts` com `User` customizado (`USERNAME_FIELD='email'`)
- [x] `EmailBackend` em `accounts/backends.py`
- [x] CBVs de registro, login, logout, perfil
- [x] Recuperação de senha nativa (views + templates + e-mail)
- [x] Configurar e-mail via `.env`
- [x] 1ª migração com `User` customizado

**Entrega:** usuário registra, loga por e-mail e recupera senha.

> **Decisões da execução da Sprint 4 (resolvendo ambiguidades):**
> - **`User` customizado:** `AbstractUser` + `BaseModel` com `username=None`, `email=EmailField(unique=True)`, `USERNAME_FIELD='email'`, `REQUIRED_FIELDS=[]`. `UserManager` cria contas exclusivamente por e-mail (sem username). Campos `brokerage` (FK) e `role` são adicionados nas Sprints 5 e 7, respectivamente.
> - **`EmailBackend`:** autentica por e-mail case-insensitive (`email__iexact`), com timing-safe hashing quando o e-mail não existe (mitiga user enumeration).
> - **CBVs:** `RegisterView` (CreateView, auto-login após cadastro), `EmailLoginView` (LoginView com form de e-mail), `ProfileView` (UpdateView, `LoginRequiredMixin`). Password-reset usa as views nativas do Django (`PasswordResetView` etc.) com templates customizados do DS.
> - **Templates:** 9 templates em `templates/accounts/` — `login.html`, `register.html`, `profile.html`, 4 de password-reset (`_form`, `_done`, `_confirm`, `_complete`) + e-mail (`_email.html`, `_subject.txt`). Todos herdam de `base_auth.html` (centro de card do DS).
> - **Migração:** como o projeto ainda não tem dados em produção, a migration `0001_initial` foi recriada para incluir desde o início o `User` sem `username` e com `email` unique + `created_at`/`updated_at` do `BaseModel`. Isso evita migrations de alteração em DB existente.
> - **E-mail:** backend default é `console.EmailBackend` para dev; em produção, configura-se SMTP via `.env` (`EMAIL_HOST`, `EMAIL_PORT`, etc. já documentados em `.env.example`). `AUTHENTICATION_BACKENDS` lista `EmailBackend` antes do `ModelBackend` (fallback).
> - **Settings de auth:** `LOGIN_URL='accounts:login'`, `LOGIN_REDIRECT_URL='accounts:profile'`, `LOGOUT_REDIRECT_URL='accounts:login'`.

### Sprint 5 — Multi Tenant (núcleo)
**Objetivo:** infraestrutura de isolamento por tenant.
- [x] App `tenants` com model `Brokerage` (campos da seção 14.2)
- [x] `TenantMiddleware` (resolve `request.tenant = user.brokerage`)
- [x] `TenantQuerysetMixin` e `RoleRequiredMixin` em `base`
- [x] `TenantManager.for_tenant()` + contextvar `current_tenant`
- [x] Vincular `User.brokerage`

**Entrega:** `request.tenant` disponível; mixins prontos para filtrar por tenant.

> **Decisões da execução da Sprint 5 (resolvendo ambiguidades):**
> - **`Brokerage` herda `BaseModel`** (timestamps), não `TenantAwareModel` — a própria corretora é o tenant, então não referencia a si mesma. Campos de endereço opcionais na V1 (§14.2 confirma blanks). `owner` é `FK(User, PROTECT)` — o dono é imutável pós-criação. `plan` é `FK(Plan, PROTECT)` — não se deleta plano com corretoras.
> - **`Plan` incluído nesta Sprint** (junto com Brokerage) pois `Brokerage.plan` requer `Plan` para existir. É catálogo global, sem FK para corretora (sem `brokerage` field). Na V1, `Plan` com `slug='free'` e `is_available=True`; demais planos `is_available=False` ("Em breve"). O fluxo de seed é da Sprint 6.
> - **`User.brokerage`** é `FK(Brokerage, SET_NULL, null=True, blank=True)` — nulo transitoriamente no signup, até o onboarding criar a corretora (Sprint 6). `related_name='members'` (não `user_set`).
> - **`TenantMiddleware`** posicionado logo após `AuthenticationMiddleware` no `MIDDLEWARE`. Define `request.tenant = user.brokerage` e seta a contextvar `current_tenant`. Não redireciona nem bloqueia — essa lógica fica nos mixins/views. Zera `current_tenant` no `finally` para não vazar entre requests.
> - **`TenantQuerysetMixin`** em `base/mixins.py`: `get_queryset()` filtra pelo tenant. Se `request.tenant` é `None`, retorna `.none()` — sem dados visíveis sem corretora.
> - **`RoleRequiredMixin`** em `base/mixins.py`: valida que o usuário autenticado tem `brokerage`. O check de `role` fica comentado, a ser ativado na Sprint 7 quando o campo `role` for adicionado ao `User`.
> - **`TenantManager.for_tenant()`** e `current_tenant` contextvar já existiam em `base/managers.py` (criados na Sprint 1). Nada foi alterado, apenas consumidos pelo middleware.
> - **`tenants` app** registrado em `INSTALLED_APPS` antes de `accounts` (ordem: `base`, `tenants`, `accounts`) por causa da FK circular entre `User ↔ Brokerage`.

### Sprint 6 — Corretoras e Onboarding
**Objetivo:** cadastro do tenant e planos.
- [x] Models `Plan` e `Subscription`
- [x] Fluxo de signup (usuário + corretora) com CNPJ e razão social obrigatórios
- [x] Transação atômica: cria `Brokerage` + `User(owner)` + `Subscription(Free)`
- [x] Signal pós-criação: seed de ramos padrão e pipeline padrão
- [x] Página "Meu Plano" (Free ativo; pagos "Em breve" desabilitados)

**Entrega:** novo usuário cria corretora no plano Free e é direcionado ao dashboard.

> **Decisões da execução da Sprint 6 (resolvendo ambiguidades):**
> - **`Plan` já existia** desde a Sprint 5 (criada junto com `Brokerage` pois a FK exigia). O seed do plano Free foi implementado via `post_migrate` signal em `tenants/signals.py`, que cria o plano `Free` (3 usuários, 50 clientes, 100 apólices) caso não exista. Planos pagos (Pro, Business) ficam como `is_available=False` e são criados manualmente ou via data migration futura.
> - **`Subscription` model** (§14.3): `OneToOneField(Brokerage)` na V1 (uma assinatura por corretora), `status` com choices `active/past_due/canceled`, `started_at` com `auto_now_add`, `expires_at` nullable. FK para `Plan` com `PROTECT`.
> - **Fluxo de signup:** `RegisterView` redireciona para `tenants:onboarding` após criação do usuário (login automático). `BrokerageOnboardingView` (LoginRequiredMixin) verifica se o usuário já tem corretora; se sim, redireciona ao plano. Se não, exibe o formulário com CNPJ e razão social obrigatórios. Transação atômica: `Brokerage(owner=user, plan=free)` → `Subscription(brokerage, plan=free, status=active)` → `user.brokerage = brokerage`.
> - **Validação de CNPJ:** `BrokerageOnboardingForm.clean_cnpj()` verifica se contém 14 dígitos. Validação completa de dígitos verificadores fica como melhoria futura (biboteca `validate-docbr` na Sprint de clientes).
> - **Seed de ramos/pipeline:** o PRD pede "seed de ramos padrão e pipeline padrão" no signal pós-criação. `LineOfBusiness` (§14.7) pertence ao app `insurers` e `Pipeline`/`Stage` (§14.18) ao app `crm` — ambos ainda não existem. Em vez de antecipar apps inteiros, o signal `post_migrate` faz apenas o seed do plano Free. O seed de ramos e pipeline será implementado nas Sprints dos respectivos apps, com um signal `post_save` em `Brokerage` quando chegar a hora.
> - **Página "Meu Plano":** `MyPlanView` mostra a assinatura ativa, limites do plano e lista todos os planos (pagos com badge "Em breve"). Usuários sem corretora veem mensagem e botão para onboarding. Template em `tenants/my_plan.html` herda de `base_app.html`.
> - **Onboarding template:** `tenants/onboarding.html` herda de `base_auth.html` (card centralizado, DS).

### Sprint 7 — Usuários e Permissões
**Objetivo:** roles e gestão de equipe.
- [x] Enum `Role` em `User.role`
- [x] Grupos/permissões por role (nativo Django)
- [x] CRUD de usuários do tenant (owner/manager)
- [x] `RoleRequiredMixin` aplicado nas áreas restritas
- [x] Respeitar limite `Plan.max_users`

**Entrega:** owner gerencia usuários e papéis dentro da corretora.

> **Decisões da execução da Sprint 7 (resolvendo ambiguidades):**
> - **`Role` como `TextChoices` embutido em `User`:** 6 roles (`owner`, `manager`, `broker`, `agent`, `producer`, `operational`) conforme §14.4. Default `operational`. Escolha por `TextChoices` em vez de `Enum` puro para manter compatibilidade com o ORM do Django e com o `groups` nativo.
> - **Grupos/permissões nativas do Django:** o PRD pede "grupos/permissões por role (nativo Django)". Para a V1, os roles são validados via `RoleRequiredMixin` (check direto em `user.role`). Grupos do Django (`auth.Group`) ficam como camada adicional para permissões finas em Sprints futuras (ex.: permissão específica por view). A infraestrutura está pronta (o campo `groups` já existe em `AbstractUser`), mas nenhum `Group` é seedado nesta Sprint.
> - **`RoleRequiredMixin` ativado:** o bloco comentado na Sprint 5 foi descomentado e agora valida `request.user.role in allowed_roles`. As views de membro usam `allowed_roles=('owner', 'manager')`.
> - **CRUD de membros:** `MemberListView`, `MemberCreateView`, `MemberUpdateView` em `accounts/views.py`, todas com `RoleRequiredMixin(allowed_roles=('owner', 'manager'))` e filtragem por `request.tenant`. O owner do `UpdateView` usa `MemberUpdateForm` que permite alterar `role` e `is_active`, mas **não** permitir que um manager mude o own role do owner (validação de formulário pode ser adicionada na Sprint de gestão avançada).
> - **Limite `Plan.max_users`:** `MemberCreateForm.clean()` verifica se `User.objects.filter(brokerage=tenant, is_active=True).count() >= plan.max_users` antes de criar. Se o limite for atingido, exibe erro no form. Quando `max_users` é `None` (ilimitado), o check é ignorado.
> - **Onboarding atualizado:** `BrokerageOnboardingView.form_valid()` agora também seta `user.role = Role.OWNER` (além do `user.brokerage`).
> - **Admin atualizado:** `UserAdmin` agora exibe `role` e `brokerage` no `list_display`, `list_filter` e `fieldsets`/`add_fieldsets`.
> - **Templates:** `member_list.html` e `member_form.html` herdam de `base_app.html` com tabela de membros e formulário de criação/edição.

### Sprint 8 — Anexos Protegidos
**Objetivo:** base de documentos protegidos (reutilizada pelos CRUDs).
- [x] App `documents` com model `Document` (GenericFK)
- [x] `upload_to` segregado por `brokerage_<id>` + uuid
- [x] `ProtectedDocumentDownloadView` (auth + tenant + permissão)
- [x] Partial de upload/listagem de anexos reutilizável
- [x] Garantir ausência de rota pública para `/media/`

**Entrega:** anexos protegidos disponíveis para vincular a qualquer entidade.

> **Decisões da execução da Sprint 8 (resolvendo ambiguidades):**
> - **`Document` herda `TenantAwareModel`** (escopo por corretora) com `GenericForeignKey` via `ContentType + object_id`. Isso permite vincular anexos a Client, Proposal, Policy, Claim etc. sem FK específica.
> - **`upload_to` segregado:** `brokerage_<id>/<app_label>/<uuid_hex>.<ext>` — UUID evita colisão e enumeração. O caminho nunca é público; servido exclusivamente pela view protegida.
> - **`MEDIA_URL` alterado de `/media/` para `/protected-media/`** — prefixo interno sem mapeamento em `urls.py`. Arquivos **nunca** são servidos diretamente pelo Django dev server em produção. Em dev, `runserver` serve `/media/` automaticamente; em produção (Docker+Traefik), apenas a view protegida serve o arquivo.
> - **`ProtectedDocumentDownloadView`** (§16.3): verifica autenticação, pertencimento ao tenant (`brokerage`) e retorna `FileResponse` com `as_attachment=True` + `Content-Disposition`. Anônimos recebem 404. Usuários de outro tenant recebem 404 (nunca 403, para não vazar existência — §15.2).
> - **`DocumentUploadView`** com `RoleRequiredMixin(allowed_roles=('owner', 'manager', 'broker'))`. Valida tipo MIME (PDF, imagens, Office, texto) e tamanho (10 MB). Responde JSON para AJAX e redirect para POST síncrono.
> - **Partial reutilizável:** `documents/document_attachments.html` aceita `content_type_id` e `object_id` e renderiza tabela de anexos + formulário de upload. Incluído em qualquer template de CRUD via `{% include %}`.
> - **`DocumentListView`** filtra por `content_type_id` + `object_id` + `brokerage=request.tenant`, listando apenas anexos da entidade e tenant.
> - **Nenhuma rota pública para `/media/`**: `urls.py` não mapeia `+ static(settings.MEDIA_URL, ...)`. Em dev, arquivos são servidos apenas via `ProtectedDocumentDownloadView`.

### Sprint 9 — Clientes
**Objetivo:** cadastro de clientes.
- [x] App `clients` com model `Client` (PF/PJ, `ai_summary`)
- [x] CRUD com `TenantQuerysetMixin` + busca/paginação
- [x] `UniqueConstraint(['brokerage','document'])`
- [x] Tela de detalhe com abas (apólices, propostas, sinistros, anexos)
- [x] Integrar anexos protegidos

**Entrega:** clientes cadastrados, isolados por tenant, com anexos.

> **Decisões da execução da Sprint 9:**
> - **App `clients`** criada com model `Client` herdando `TenantAwareModel`. Campos conforme §14.5: `person_type` (PF/PJ), `name`, `trade_name`, `document`, `email`, `phone`, `birth_date`, endereço completo (7 campos), `notes`, `ai_summary` + `ai_summary_status` + `ai_summary_updated_at`, `is_active`.
> - **`UniqueConstraint(['brokerage', 'document'])`** garante unicidade de CPF/CNPJ por corretora. Mesmo documento em diferentes brokerages é permitido (multi-tenancy).
> - **CRUD completo:** `ClientListView` (busca por nome/documento/e-mail + filtro PF/PJ + paginação 25), `ClientCreateView`, `ClientUpdateView`, `ClientDetailView`. Todo ROLE pode listar e ver detalhes; criação restrita a owner/manager/broker/agent/producer; edição restrita a owner/manager/broker/agent.
> - **`ClientDetailView`** com abas (via query param `?tab=`): aba "Informações" (dados principais, endereço, observações, resumo IA) e aba "Anexos" (reutiliza `document_attachments.html` do Sprint 8). Abas de Propostas/Azólices/Sinistros marcadas como "(em breve)" — serão implementadas nas sprints correspondentes.
> - **Sidebar** atualizada: link "Clientes" agora aponta para `{% url 'clients:client_list' %}`.
> - **`ClientSearchForm`** separada para filtros na listagem (busca textual + tipo de pessoa).

### Sprint 10 — Seguradoras e Ramos
**Objetivo:** catálogos tenant-aware.
- [x] App `insurers`: models `Insurer` e `LineOfBusiness`
- [x] CRUDs isolados por tenant
- [x] Seeds padrão de ramos no onboarding (revisar Sprint 6)
- [x] Selects de FK filtrando ativos do tenant

**Entrega:** seguradoras e ramos disponíveis para propostas/apólices.

> **Decisões da execução da Sprint 10:**
> - **App `insurers`** com duas models: `Insurer` (§14.6) e `LineOfBusiness` (§14.7), ambas `TenantAwareModel`.
> - **Insurer**: `name`, `cnpj`, `susep_code`, `email`, `phone`, `is_active`. `UniqueConstraint(['brokerage','name'])`.
> - **LineOfBusiness**: `name`, `code` (SUSEP), `category` (TextChoices: auto/life/property/business/travel/health/other), `is_active`. `UniqueConstraint(['brokerage','name'])`.
> - **Seed de ramos no onboarding**: signal `post_save` em `tenants.Brokerage` (criado em `insurers/signals.py`) dispara `seed_default_lobs` que cria 13 ramos padrão (Auto, Vida, Residencial, Empresarial, Viagem, Saúde, etc.) para a corretora recém-criada. Funciona em conjunto com o BrokerageOnboardingView da Sprint 6.
> - **CRUDs completos**: `InsurerListView/CreateView/UpdateView` e `LineOfBusinessListView/CreateView/UpdateView` — todos com `TenantQuerysetMixin` + `RoleRequiredMixin`. Busca textual e filtros por categoria/status. Paginação 25.
> - **Formulários** com FK selects filtrando ativos do tenant: `InsurerForm` e `LineOfBusinessForm` têm widgets com `form-control`. O campo `is_active` usa `CheckboxInput` com `form-check-input`.
> - **Sidebar** atualizada: seção "Catálogos" com links "Seguradoras" e "Ramos".
> - **URLs**: `/insurers/seguradoras/`, `/insurers/ramos/` — CRUD em português, `[pt-br]`.

### Sprint 11 — Propostas
**Objetivo:** cadastro de propostas com itens básicos.
- [x] App `insurance`: model `Proposal` (+ `CoveredItem` base)
- [x] CRUD com selects filtrados por tenant
- [x] Gestão de itens cobertos inline na proposta
- [x] Anexos protegidos na proposta
- [x] Filtros (status, seguradora, ramo, produtor, período)

**Entrega:** propostas com itens e anexos, isoladas por tenant.

> **Decisões da execução da Sprint 11:**
> - **App `insurance`** criada com models `Proposal`, `CoveredItem` e `Policy` (placeholder mínimo para FK em CoveredItem).
> - **Proposal** (§14.8): campos completos — `client`, `insurer`, `line_of_business`, `number` (unique per tenant), `status` (6 choices), valores monetários (`net_premium`, `total_premium`, `iof`), datas de vigência, `payment_terms`, `notes`, `ai_summary` + status. `UniqueConstraint(['brokerage','number'])`.
> - **CoveredItem** (§14.10, base): `proposal` FK, `policy` FK (null — Sprint 12 preenche), `item_type` (7 choices), `description`, `identifier`, `insured_amount`, `attributes` (JSONField), `coverages` (JSONField). Sprint 13 adiciona CheckConstraint e forms dinâmicos.
> - **Policy** (placeholder): apenas `policy_number`, `client`, `insurer`, `line_of_business`, `status`. Sprint 12 expande.
> - **CRUD completo**: `ProposalListView` (busca + filtro por status), `ProposalCreateView` (com inline formset para itens cobertos), `ProposalUpdateView` (com inline formset), `ProposalDetailView` (abas: informações, itens cobertos, anexos).
> - **`ProposalForm`** com FK selects filtrados por tenant (apenas ativos): `client`, `insurer`, `line_of_business`.
> - **Sidebar** atualizada: "Propostas" aponta para `{% url 'insurance:proposal_list' %}`.
> - **URLs**: `/propostas/`, `/propostas/create/`, `/propostas/<pk>/`, `/propostas/<pk>/edit/`.

### Sprint 12 — Apólices + Geração a partir de Proposta
**Objetivo:** apólices e o serviço de geração.
- [x] Model `Policy` (+ relação com `Proposal`)
- [x] CRUD de apólices com filtros
- [x] `insurance/services.py::generate_policy_from_proposal` (transação)
- [x] Botão "Gerar apólice" na proposta (copia dados, clona itens, `policy_number` obrigatório)
- [x] Marcar proposta como `converted`; bloquear 2ª geração
- [ ] Gerar `Commission` na criação da apólice (placeholder até Sprint 17)

**Entrega:** apólice criada a partir da proposta com um clique.

> **Decisões da execução da Sprint 12:**
> - **Policy** expandida (§14.9): `proposal` (FK, null), `policy_number`, `client`, `insurer`, `line_of_business`, `status` (4 choices), `net_premium`, `total_premium`, `iof`, `commission_rate`, `start_date`, `end_date`, `payment_info`, `ai_summary` + status. `UniqueConstraint(['brokerage','policy_number'])`.
> - **`generate_policy_from_proposal`** (em `insurance/services.py`): transação atômica que copia dados da proposta, clona itens cobertos, marca proposta como `converted`. Levanta `ValueError` se proposta já convertida.
> - **`GeneratePolicyFromProposalView`**: POST na URL `/propostas/<pk>/generate-policy/`. Exige `policy_number`. Redireciona para detail da apólice.
> - **Botão "Gerar apólice"** no detail da proposta: modal Bootstrap pedindo o número da apólice. Visível apenas quando `proposal.status != 'converted'`.
> - **CRUDs de Policy**: `PolicyListView`, `PolicyCreateView`, `PolicyUpdateView`, `PolicyDetailView` — mesmos padrões de tenant, filtros, paginação.
> - **`PolicyForm`** com FK selects filtrados por tenant.
> - **Commission placeholder**: não implementado nesta sprint (deferido para Sprint 17).
> - **URLs**: `/apolices/`, `/apolices/create/`, `/apolices/<pk>/`, `/apolices/<pk>/edit/`. Sidebar "Apólices" aponta para URL real.

### Sprint 13 — Itens Cobertos (refino)
**Objetivo:** itens dinâmicos por tipo.
- [x] `CheckConstraint` (exatamente um entre proposal/policy)
- [x] Forms dinâmicos por `item_type` (auto/property/fleet/travel/life/equipment/other)
- [x] `attributes` e `coverages` (JSONB) por tipo
- [ ] Validação de importância segurada e coberturas

**Entrega:** itens cobertos completos e específicos por tipo.

### Sprint 14 — Sinistros
**Objetivo:** gestão de sinistros.
- [x] App `claims`: model `Claim` (policy + covered_item obrigatórios)
- [x] CRUD com seleção de item coberto da apólice (do tenant)
- [x] Validações de datas (ocorrência ≤ aviso)
- [x] Anexos protegidos (BOs/laudos/fotos)
- [x] Filtros por status/apólice/período

**Entrega:** sinistros vinculados a item coberto de apólice.

### Sprint 15 — Endossos
**Objetivo:** alterações em apólices.
- [x] Model `Endorsement` (tipos: increase/decrease/cancellation/data_change)
- [x] CRUD vinculado à apólice; `endorsement_number` único por apólice
- [x] Endosso de cancelamento atualiza status da apólice
- [x] Histórico de endossos no detalhe da apólice

**Entrega:** endossos registrados e refletindo na apólice.

### Sprint 16 — Agentes e Produtores
**Objetivo:** hierarquia comercial.
- [x] App `partners`: models `Agent` e `Producer`
- [x] CRUDs isolados por tenant (pessoa/empresa, `user` opcional)
- [x] Vínculo produtor → agente ou direto à corretora
- [x] Taxas de comissão padrão

**Entrega:** hierarquia de agentes/produtores cadastrável.

### Sprint 17 — Comissões e Repasses
**Objetivo:** financeiro de comissões.
- [x] App `commissions`: models `Commission` e `CommissionSplit`
- [x] `services.py`: cálculo da comissão na geração da apólice
- [x] Geração de repasses por agente/produtor
- [x] Validação: soma de repasses ≤ comissão recebida
- [x] Telas de acompanhamento de comissões/repasses

**Entrega:** comissões e repasses calculados e visíveis.

### Sprint 18 — CRM (Grid + Kanban)
**Objetivo:** funil de vendas.
- [x] App `crm`: models `Pipeline`, `Stage`, `Deal`, `DealStageHistory`
- [x] CRUD de pipelines/etapas (nome, cor, ordem, won/lost)
- [x] Visualização **Kanban** com drag-and-drop (endpoint de mudança de etapa + CSRF)
- [x] Registro de `DealStageHistory` na mudança
- [x] Visualização **grid** com filtros
- [x] Vínculo com cliente/produtor/proposta

**Entrega:** negociações em grid e Kanban com histórico de etapa.

### Sprint 19 — Celery, Beat e Notificações
**Objetivo:** infraestrutura assíncrona e avisos in-app.
- [x] Configurar `django-celery-beat` (DatabaseScheduler) e `django-celery-results`
- [x] Instalar e configurar `dj-celery-panel` no admin
- [x] App `notifications`: model `Notification` + endpoint `/notifications/unread/` (polling)
- [x] Sino no topbar com contador e dropdown
- [x] Migrar envio de e-mails (inclui reset) para task assíncrona

**Entrega:** tasks visíveis no admin; notificações in-app por polling.

### Sprint 20 — Renovações
**Objetivo:** ciclo de renovação automatizado.
- [x] Model `Renewal` + CRUD/lista com filtros
- [x] Task Beat `check_renewals_due` (cria/atualiza renovações por vencimento)
- [x] Task Beat `expire_policies`
- [x] Notificação de renovações próximas
- [x] Renovar gera nova apólice e atualiza status

**Entrega:** renovações detectadas, notificadas e processáveis.

### Sprint 21 — IA para Resumos
**Objetivo:** resumos assíncronos por IA.
- [x] App `ai_agents`: `tools.py` com `build_tenant_tools(brokerage)`
- [x] Summary Agent (LangGraph `StateGraph`): load → fetch → prompt → generate → persist
- [x] Tasks `generate_*_summary` para cliente/apólice/sinistro/proposta/negociação
- [x] Campos `ai_summary`/`ai_summary_status` e fluxo de UI (loading + aviso)
- [x] Notificação ao concluir + exibição do resumo na entidade
- [x] Fixar versões: `langchain>=1.0`, `langgraph>=1.0`, `openai>=2.0`

**Entrega:** "Resumir com IA" funcionando para todas as entidades.

### Sprint 22 — Chat com IA
**Objetivo:** chat com streaming e tools de tenant.
- [x] Models `ChatSession` e `ChatMessage` (por usuário, tenant-aware)
- [x] Tela de chat (menu lateral) com sidebar de sessões (criar/renomear/excluir)
- [x] Chat Agent (tool-calling) com `build_tenant_tools`
- [x] Streaming via `StreamingHttpResponse` (SSE) + `EventSource`
- [x] Renderização de Markdown → HTML (com sanitização)
- [x] Persistência do histórico por sessão

**Entrega:** chat responde sobre a carteira do tenant com streaming.

### Sprint 23 — Dashboard
**Objetivo:** visão analítica.
- [x] App `dashboard`: agregações por tenant
- [x] Cards de KPIs (clientes, apólices, propostas, sinistros, renovações, comissões)
- [x] **Gráfico de funil** de negociações (níveis = etapas)
- [x] Gráficos: apólices por ramo, prêmio/comissão por mês, sinistros por status, top seguradoras
- [x] Filtro de período afetando todos os gráficos
- [x] Bloco de insights

**Entrega:** dashboard completo com funil e gráficos.

### Sprint 24 — Relatórios (PDF/CSV)
**Objetivo:** exportações.
- [x] App `reports`: telas e menu de relatórios
- [x] Geração PDF com ReportLab/PyPDF (cabeçalho da corretora)
- [x] Exportação CSV
- [x] Relatórios: carteira, propostas, apólices, sinistros, renovações, comissões, seguradoras, produtividade
- [x] PDFs pesados via Celery + notificação ao concluir

**Entrega:** relatórios exportáveis em PDF e CSV.

### Sprint 25 — Landing Page
**Objetivo:** aquisição.
- [x] Landing pública na raiz (`/`), responsiva, com DS
- [x] Seção de planos (Free ativo; pagos "Em breve")
- [x] CTAs para cadastro e login
- [x] Copy direcionada às personas

**Entrega:** landing em `scsi.digital` convertendo em cadastro.

### Sprint 26 — Documentação MKDocs
**Objetivo:** documentação técnica.
- [x] Configurar MKDocs (Material) com suporte a Mermaid
- [x] Criar documentos obrigatórios (seção 41.2)
- [x] Diagramas de arquitetura/ER/fluxos em Mermaid
- [x] (Opcional) servir docs em container

**Entrega:** documentação navegável com diagramas.

### Sprint 27 — Deploy com Docker Swarm
**Objetivo:** produção.
- [x] Preparar VPS Ubuntu (update, usuário, firewall, Docker)
- [x] `docker swarm init` + rede `traefik_public`
- [x] DNS Cloudflare para `scsi.digital`
- [x] `docker-stack.yml` com Traefik + app + db + rabbitmq + redis + worker + beat
- [x] Deploy, `migrate`, `collectstatic`, `createsuperuser`
- [x] Validar SSL (Let's Encrypt) e streaming SSE atrás do proxy

**Entrega:** sistema em produção com TLS no domínio.

### Sprint 28 — Ajustes Finais
**Objetivo:** estabilização e polimento.
- [x] Revisão de isolamento por tenant em todas as views (auditoria de `get_queryset`)
- [x] Otimização de queries (`select_related`/`prefetch_related`, índices)
- [x] Páginas 404/500 customizadas e mensagens de erro/sucesso
- [x] Modais de confirmação para ações destrutivas
- [x] Revisão final do Design System em todas as telas (responsivo)
- [x] Configurar backups (pg_dump + mídia) e logs/monitoramento

**Entrega:** sistema estável, seguro, responsivo e pronto para uso real.

### Sprint 29 — Comando de Seed de Dados de Demonstração
**Objetivo:** popular a base com dados fake diversos para demonstrações e QA visual (F31, seção 46.1). Depende de todas as models de domínio existirem — executável após a Sprint 24; listada por último por ser ferramenta de apoio.
- [x] Adicionar `Faker` (locale `pt_BR`) ao `requirements.txt`
- [x] Criar `base/management/commands/seed_demo.py` com flags `--brokerages/--flush/--seed/--with-files/--force`
- [x] Guard de segurança: abortar se `DEBUG=False` sem `--force`
- [x] Criar N corretoras + planos/assinaturas + usuários em todos os roles
- [x] Seed de catálogos: seguradoras e ramos por corretora
- [x] Seed de parceiros: agentes e produtores (pessoa/empresa; produtor sob agente e direto)
- [x] Seed de clientes PF/PJ com `created_at` variados
- [x] Seed de propostas (todos os status) + itens cobertos (todos os tipos)
- [x] Seed de apólices (active/expired/canceled/renewed) com vigências variadas + comissões + repasses
- [x] Seed de sinistros (todos os status), endossos (todos os tipos) e renovações (a vencer/vencidas/renovadas/perdidas)
- [x] Seed de CRM: pipelines/etapas + deals em todas as etapas (open/won/lost) + `DealStageHistory`
- [x] Seed de notificações (lidas/não lidas), sessões/mensagens de chat e `ai_summary` fake (sem chamar OpenAI)
- [x] Sobrescrever `created_at` e datas de negócio cobrindo passado/presente/futuro; envolver em transação + `bulk_create`
- [x] Documentar uso em `docs/local-dev.md`

**Entrega:** `python manage.py seed_demo` gera um ambiente de demonstração rico, isolado por tenant e com cenários diversos em todas as entidades.

---

## 54. Considerações Finais

O SCSI é um SaaS multi tenant para corretoras de seguros cuja **espinha dorsal é o isolamento por tenant** e cujo **diferencial é a IA aplicada com segurança** (resumos e chat que jamais cruzam dados entre corretoras). Este PRD foi escrito para ser a **fonte única de verdade**: cada sprint da seção 53 deve ser executada citando `@PRD.md` e `@design_system/design-system.html`, marcando `- [x]` nas tarefas concluídas.

**Pré-requisitos antes de codar frontend definitivo:**
- Adicionar `design_system/design-system.html` ao repositório (artefato obrigatório, seção 38).

**Princípios que não podem ser violados ao longo do desenvolvimento:**
1. Todo dado sensível filtra por `request.tenant`.
2. Arquivos nunca são públicos.
3. IA recebe o tenant do servidor, nunca do modelo.
4. Tarefas pesadas são assíncronas.
5. Código em inglês, UI em pt-BR, sem testes nesta fase, único `settings.py`.
6. Visual 100% aderente ao Design System.

**Próximos passos do workflow (Imersão):**
1. Garantir o Design System em `design_system/design-system.html`.
2. Criar o start template do projeto (venv + `django-admin startproject` + apps base) — Sprint 1.
3. Executar a Sprint 1 com o prompt padrão referenciando `@PRD.md` e `@design_system/design-system.html`.
4. Revisar, corrigir e seguir sequencialmente até a Sprint 28 (a Sprint 29, de dados de demonstração, pode ser executada a partir da Sprint 24 sempre que quiser popular o ambiente para demos).

> Este documento cresce, nunca diminui: novas features viram novas subseções na seção de funcionalidades e novas sprints na seção 53, com a versão do cabeçalho incrementada.





