# SCSI — Sistema de Corretora de Seguros Inteligente

Bem-vindo à documentação técnica do **SCSI**, um SaaS multi tenant para corretoras de seguros com IA aplicada (resumos e chat que jamais cruzam dados entre corretoras).

## Navegação

| Documento | Conteúdo |
|---|---|
| [Arquitetura](architecture.md) | Visão geral, stack, camadas, infraestrutura |
| [Multi Tenant](multi-tenant.md) | Estratégia de isolamento por tenant e regras |
| [Modelo de Domínio](domain-model.md) | Entidades, ER e relacionamentos |
| [Permissões](permissions.md) | Roles, permissões e segurança |
| [Arquivos Protegidos](protected-media.md) | Como funciona o serving de arquivos protegidos |
| [Agentes de IA](ai-agents.md) | Agentes de resumo e chat, tools isoladas, custos |
| [Celery e Tasks](celery-tasks.md) | Tasks, beat, fluxo de resumo e notificações |
| [Variáveis de Ambiente](env-vars.md) | `.env` completo com referência |
| [Desenvolvimento Local](local-dev.md) | subir o ambiente com Docker Compose |
| [Deploy](deploy.md) | Deploy com Docker Swarm + Traefik (passo a passo) |
| [Backup e Restore](backup.md) | Estratégia e procedimentos de backup/restore |
| [Runbook](runbook.md) | Operação, incidentes, logs e monitoramento |

## Stack principal

- **Backend:** Django 6.0 + Python 3.13
- **Banco:** PostgreSQL 16
- **Filas:** Celery + RabbitMQ + Redis
- **IA:** LangChain + LangGraph + OpenAI
- **Frontend:** Bootstrap 5 com Design System customizado
- **Infra:** Docker + Docker Swarm + Traefik + Let's Encrypt