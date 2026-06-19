# Permissões e Segurança

## Roles de Usuário

O model `User` possui o campo `role` com os seguintes valores:

| Role | Descrição | Acesso |
|---|---|---|
| `owner` | Dono da corretora | Total (CRUD em tudo + gestão de plano) |
| `manager` | Gerente | CRUD em entidades, visualiza relatórios e comissões |
| `broker` | Corretor | CRUD em clientes, propostas, apólices, sinistros |
| `agent` | Agente parceiro | Visualiza suas comissões e clientes vinculados |
| `producer` | Produtor | Visualiza suas comissões e clientes vinculados |
| `operational` | Operacional | CRUD em entidades, sem acesso a financeiro |

## Controle de acesso

### `TenantQuerysetMixin`

Automaticamente filtra todos os querysets por `request.tenant` (a corretora do usuário). Se o usuário não tem corretora, o queryset retorna vazio.

```python
class MinhaView(TenantQuerysetMixin, ListView):
    model = Client
    # get_queryset() já filtra por brokerage automaticamente
```

### `RoleRequiredMixin`

Bloqueia o acesso se o `request.user.role` não estiver em `allowed_roles`.

```python
class MinhaView(RoleRequiredMixin, TenantQuerysetMixin, CreateView):
    allowed_roles = ['owner', 'manager']
```

## Padrões de segurança

| Prática | Implementação |
|---|---|
| Isolamento por tenant | FK `brokerage` + `TenantQuerysetMixin` + `TenantMiddleware` |
| Arquivos protegidos | `MEDIA_URL=/protected-media/` — nunca servidos estaticamente |
| IA isolada | `build_tenant_tools(brokerage)` — tools recebem a corretora do server |
| SSL/TLS | Traefik + Let's Encrypt em produção |
| CSRF | Django CSRF padrão + `CSRF_TRUSTED_ORIGINS` |
| Senhas | Django `AbstractUser` com hashers padrão |
| Validação de input | Forms + Model validation + `CheckConstraint` |
| Soft delete | `is_active` em entidades críticas (nunca exclusão física) |

## URLs e namespaces

| App | Prefixo URL | Função |
|---|---|---|
| `core` | `/` | Landing page (redirect se autenticado) |
| `accounts` | `/accounts/` | Login, logout, registro, perfil |
| `tenants` | `/tenants/` | Onboarding de corretora, planos |
| `dashboard` | `/dashboard/` | Dashboard com KPIs e gráficos |
| `clients` | `/clientes/` | CRUD de clientes |
| `insurers` | `/seguradoras/` | CRUD de seguradoras e ramos |
| `insurance` | `/insurance/` | Propostas, apólices, endossos, renovações |
| `claims` | `/sinistros/` | CRUD de sinistros |
| `partners` | `/parceiros/` | Agentes e produtores |
| `commissions` | `/comissoes/` | Comissões e repasses |
| `crm` | `/crm/` | Pipeline, Kanban, deals |
| `notifications` | `/notifications/` | Notificações (unread count) |
| `ai` | `/ai/` | Resumo de IA + chat |
| `documents` | `/documents/` | Upload e download de arquivos protegidos |
| `reports` | `/relatorios/` | Exportação PDF/CSV |