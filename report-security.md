# Relatório de Auditoria de Segurança — SCSI Imersão V1

**Branch:** `sprint_29`  
**Hash:** `43cd33d`  
**Data:** 02/06/2026  

---

## Sumário Executivo

| Categoria | Total | Crítica | Alta | Média | Baixa | Info |
|-----------|-------|---------|------|-------|-------|------|
| Autenticação & Sessão | 2 | 0 | 1 | 1 | 0 | 0 |
| Autorização & RBAC | 0 | 0 | 0 | 0 | 0 | 0 |
| Configuração Django | 2 | 0 | 0 | 2 | 0 | 0 |
| Infraestrutura | 4 | 0 | 2 | 1 | 1 | 0 |
| AI Agent | 3 | 1 | 1 | 1 | 0 | 0 |
| Documentos & Upload | 1 | 0 | 0 | 1 | 0 | 0 |
| Dependências | 2 | 0 | 1 | 0 | 1 | 0 |
| **Total** | **14** | **1** | **5** | **6** | **2** | **0** |

---

## 1. Configuração Django (settings.py)

### 1.1 [MÉDIO] SECRET_KEY com default inseguro

**Arquivo:** `core/settings.py:30`

```python
SECRET_KEY = env('SECRET_KEY', default='django-insecure-change-me-in-production')
```

O default `django-insecure-change-me-in-production` é um placeholder explícito. Se o `.env` não existir ou a variável não for carregada em algum ambiente, o Django aceitará essa chave conhecida, permitindo forjamento de sessões e assinaturas CSRF.

**Recomendação:** Remover o `default` e deixar o sistema falhar cedo se `SECRET_KEY` não estiver definida. Ou validar em `AppConfig.ready()` se o valor é o placeholder.

### 1.2 [MÉDIO] DEBUG com default False pode mascarar configuração incorreta

**Arquivo:** `core/settings.py:33`

```python
DEBUG = env('DEBUG')
```

**Status:** Visa o comportamento correto — DEBUG lê do ambiente. Sem default, falha se ausente, que é o comportamento seguro. **Nenhuma ação necessária**, apenas monitoramento para garantir que DEBUG=True nunca vá para produção.

### 1.3 [MÉDIO] CORS/CSRF sem restrição de origem explícita

**Arquivo:** `core/settings.py:37`

```python
CSRF_TRUSTED_ORIGINS = env('CSRF_TRUSTED_ORIGINS', default=[])
```

Depende exclusivamente do `.env` para configurar origens confiáveis. Caso `CSRF_TRUSTED_ORIGINS` não seja definido em produção, requisições POST legítimas podem ser rejeitadas (comportamento seguro por padrão). Não há `django-cors-headers` instalado — não existe configuração de CORS.

**Recomendação:** Confirmar que `CSRF_TRUSTED_ORIGINS` está definido no `.env` de produção. Avaliar se `django-cors-headers` é necessário para chamadas de API de frontends separados.

### 1.4 [INFO] Content Security Policy (CSP) ausente

Não há `django-csp` instalado ou cabeçalho `Content-Security-Policy` configurado. O sistema depende exclusivamente do Django SecurityMiddleware sem proteção CSP.

**Recomendação:** Baixa prioridade para V1. Considerar `django-csp` em versão futura para mitigar XSS.

---

## 2. Autenticação

### 2.1 [ALTA] Taxa de login (rate limit) ausente

O endpoint `/accounts/login/` (`EmailLoginView`) não possui proteção contra ataques de força bruta. O formulário de login (EmailAuthenticationForm) estende o AuthenticationForm do Django sem CAPTCHA, rate limit, ou bloqueio por tentativas.

**Recomendação:** Implementar `django-axes` ou `django-ratelimit` para bloquear após N tentativas falhas. Alternativamente, integrar reCAPTCHA no formulário de login.

### 2.2 [MÉDIO] Senhas em texto plano via GET param — não observado

**Status:** As views de criação de usuário (RegisterView, MemberCreateView) usam `UserCreationForm`, que lida com senhas via POST e armazena hash. Implementação correta. **Nenhuma ação necessária.**

### 2.3 [INFO] Logout sem confirmação POST

A URL `/accounts/logout/` usa `LogoutView` do Django, que faz logout via GET (padrão do Django). Embora seja o comportamento default aceito, versões mais recentes do Django permitem forçar POST.

**Recomendação:** Mudar `LogoutView.as_view()` para `LogoutView.as_view(next_page=..., http_method_names=['post'])` e usar formulário POST no template.

---

## 3. Backend de Autenticação

### 3.1 [BAIXO] Timing attack mitigado corretamente

**Arquivo:** `accounts/backends.py:17`

```python
except UserModel.DoesNotExist:
    UserModel().set_password(password)
    return None
```

A mitigação de timing attack está presente: mesmo quando o e-mail não existe, o hasher é executado. **Implementação correta.**

---

## 4. Autorização e RBAC

### 4.1 [INFO] Modelo de RBAC consistente

Todas as views de alteração de dados usam `RoleRequiredMixin` com `allowed_roles` adequadamente restritos:

| Operação | Roles Permitidas |
|----------|-----------------|
| Criar membro | owner, manager |
| Criar/editar proposta | owner, manager, broker, agent, producer |
| Criar/editar apólice | owner, manager, broker |
| Upload de documentos | owner, manager, broker |
| Visualização geral | owner, manager, broker, agent, producer, operational |
| Gerar resumo IA | owner, manager, broker, agent, producer |

**Nenhuma ação necessária.** A segregação por papel está bem desenhada.

### 4.2 [INFO] Isolamento por tenant (multi-tenancy) correto

`TenantMiddleware` + `TenantAwareModel` + `TenantQuerysetMixin` garantem isolamento completo. Todas as queries de listagem/detalhe filtram por `brokerage`. Models sensíveis (Client, Policy, Proposal, Claim, etc.) herdam de `TenantAwareModel`.

---

## 5. Document Upload e Download

### 5.1 [MÉDIO] Validação de MIME type baseada no header HTTP

**Arquivo:** `documents/forms.py:41`

```python
if hasattr(f, 'content_type') and f.content_type and f.content_type not in ALLOWED_MIME_TYPES:
    raise ValidationError('Tipo de arquivo não permitido.')
```

A validação de tipo usa `content_type` do upload, que é enviado pelo cliente e pode ser facilmente falsificado. Um atacante pode renomear um `.exe` para `.pdf` com `Content-Type: application/pdf`.

**Recomendação:** Adicionar verificação real de tipo via `python-magic` (libmagic) para inspecionar os bytes reais do arquivo. Ou implementar validação de assinatura MIME no backend.

### 5.2 [INFO] Tamanho máximo de upload: 10 MB

**Arquivo:** `documents/forms.py:23`

```python
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB
```

Limite razoável. **Nenhuma ação necessária.**

### 5.3 [INFO] Download de documentos protegido

`ProtectedDocumentDownloadView` verifica autenticação `and` tenant `and` propriedade do documento. Implementação correta.

---

## 6. AI Agent — Risco Elevado

### 6.1 [CRÍTICO] CSRF desabilitado em endpoint de sumarização

**Arquivo:** `ai_agents/views.py:37`

```python
@method_decorator(csrf_exempt, name='dispatch')
class GenerateSummaryView(RoleRequiredMixin, View):
```

O decorator `@csrf_exempt` desativa a proteção CSRF em um endpoint que modifica estado (`POST` para iniciar geração de resumo). Embora protegido por `RoleRequiredMixin`, isso expõe o endpoint a ataques CSRF: um site malicioso pode fazer um usuário autenticado disparar N resumos simultâneos.

**Recomendação:** Remover `@csrf_exempt`. O formulário de trigger deve incluir `{% csrf_token %}`.

### 6.2 [ALTA] Chat agent — dados sensíveis enviados à OpenAI

**Arquivos:**
- `ai_agents/agents.py:199` — `ChatOpenAI(model='gpt-4o-mini')`
- `ai_agents/tools.py` — acesso a dados de clientes, apólices, sinistros

Dados sensíveis (CPF/CNPJ de clientes, valores de apólices, dados de sinistros) são enviados para a API da OpenAI para geração de resumos e respostas de chat.

**Riscos:**
- Dados trafegam para servidores terceiros (OpenAI) sem criptografia específica do cliente
- OpenAI pode usar dados para treinamento (dependendo do contrato/plano)
- Sem anonimização antes do envio

**Recomendação:**
1. Verificar contrato com OpenAI para garantir cláusula de `no-training` (API enterprise)
2. Implementar anonimização/pseudonimização antes de enviar dados pessoais
3. Adicionar aviso de consentimento no UI: "Dados serão processados por IA externa"
4. Considerar modelo self-hosted (ex.: via Ollama, vLLM) para dados sensíveis

### 6.3 [MÉDIO] Chave OpenAI armazenada em variável de ambiente

**Arquivo:** `core/settings.py:227`

```python
OPENAI_API_KEY = env('OPENAI_API_KEY', default='')
```

**Status:** Padrão aceitável, mas sem criptografia em repouso para a chave.

**Recomendação:** Usar `django-environ` com suporte a `.env` criptografado ou um vault externo (HashiCorp Vault, AWS Secrets Manager) em produção.

### 6.4 [BAIXO] Streaming async sem proteção de injeção de prompt

**Arquivo:** `ai_agents/views.py:210-234`

O chat streaming aceita mensagens do usuário e as envia diretamente para o LLM. Não há sanitização de entrada para ataques de prompt injection. Um usuário malicioso (autenticado) pode tentar extrair dados de outros tenants via injeção no system prompt.

**Recomendação:** Adicionar validação de entrada (limite de caracteres, bloqueio de padrões suspeitos) e reforçar o system prompt com instruções anti-jailbreak.

---

## 7. Infraestrutura

### 7.1 [ALTA] PostgreSQL sem rede isolada (docker-compose)

**Arquivo:** `docker-compose.yml:30`

```yaml
ports:
  - '5432:5432'
```

O banco de dados PostgreSQL está exposto na porta 5432 para o host. Em desenvolvimento local pode ser aceitável, mas a configuração é perigosa se copiada para qualquer ambiente acessível externamente.

**Recomendação:** Remover a seção `ports` do serviço `db` no docker-compose.yml de produção. O `docker-stack.yml` (Swarm) já usa rede `internal` corretamente.

### 7.2 [ALTA] RabbitMQ exposto publicamente

**Arquivo:** `docker-compose.yml:43`

```yaml
ports:
  - '5672:5672'
  - '15672:15672'
```

RabbitMQ está exposto em duas portas para o host. A porta 15672 é a interface de gerenciamento que, se acessível externamente com credenciais default (`guest`), permite controle total do broker.

**Recomendação:**
1. Em produção, não expor portas do RabbitMQ publicamente
2. Garantir que `RABBITMQ_DEFAULT_USER`/`RABBITMQ_DEFAULT_PASS` não sejam `guest`
3. Usar apenas rede `internal` (como já feito no `docker-stack.yml`)

### 7.3 [MÉDIO] Redis sem autenticação

**Arquivo:** `docker-compose.yml:47`

```yaml
redis:
  image: redis:7
  ports:
    - '6379:6379'
```

Redis exposto sem senha nem `--requirepass`. Em produção, Redis desprotegido permite que qualquer pessoa leia/escreva no cache, podendo afetar resultados de tasks e sessões se usado como backend de sessão.

**Recomendação:**
1. Configurar `--requirepass` no Redis
2. Remover mapeamento de porta pública
3. Usar `CELERY_RESULT_BACKEND` com senha

### 7.4 [MÉDIO] Dockerfile roda como root

**Arquivo:** `Dockerfile:1`

```dockerfile
FROM python:3.13-slim
...
ENTRYPOINT ["./entrypoint.sh"]
```

O container roda como usuário `root` (padrão). Isso viola o princípio de menor privilégio.

**Recomendação:** Adicionar `RUN adduser --system --no-create-home appuser && USER appuser` no Dockerfile, ajustando permissões dos diretórios media/ e staticfiles/ conforme necessário.

### 7.5 [MÉDIO] healthcheck do PostgreSQL vaza usuário no comando

**Arquivo:** `docker-compose.yml:32`

```yaml
healthcheck:
  test: ['CMD-SHELL', 'pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}']
```

**Status:** Comando aceitável para ambiente local. Em produção, o Swarm healthcheck segue outro padrão.

### 7.6 [ALTA] Imagem de produção aponta para registry placeholder

**Arquivo:** `docker-stack.yml:39`

```yaml
image: ghcr.io/pycodebr/scsi:latest
```

`registry.example.com` é claramente um placeholder. Risco de deploy com imagem incorreta ou inexistente se não substituído.

**Recomendação:** Garantir que o CI/CD substitua esse valor ou que haja verificação de imagem válida antes do deploy.

---

## 8. Dependências

### 8.1 [ALTA] Django 6.0.5 — versão recente, sem CVEs conhecidas

**Arquivo:** `requirements.txt:16`

```
Django==6.0.5
```

**Status:** Django 6.0.x é a versão mais recente estável. CVEs conhecidas até a data da auditoria: N/A. **Nenhuma ação necessária**, mas monitorar.

### 8.2 [MÉDIO] Dependências não auditadas

77 pacotes no total, sem ferramenta de auditoria de vulnerabilidades (ex.: `pip-audit`, `safety`, `bandit`) integrada ao pipeline.

**Recomendação:**
1. Adicionar `pip-audit` ao CI/CD para verificar vulnerabilidades conhecidas
2. Usar `bandit` para análise estática de segurança
3. Considerar `django-secure` ou `django-check-seo` para checagens complementares

### 8.3 [INFO] ReportLab 4.5.1 sem risco conhecido

ReportLab está presente para geração de PDFs. Versão recente. **Nenhuma ação necessária.**

---

## 9. Gestão de Secrets

### 9.1 [MÉDIO] .env.example contém placeholder inseguro

**Arquivo:** `.env.example`

```
SECRET_KEY=troque-esta-chave-em-producao
POSTGRES_PASSWORD=troque-esta-senha
EMAIL_HOST_PASSWORD=troque-esta-senha
```

**Status:** Placeholder explícito é esperado em `.env.example` e `.env` está no `.gitignore`. Monitorar para garantir que `.env` real nunca seja versionado.

---

## 10. Checklist de Conformidade OWASP Top 10 (2021)

| ID | Categoria | Status | Observação |
|----|-----------|--------|------------|
| A01 | Broken Access Control | ✔️ OK | RBAC + Tenant isolation implementados |
| A02 | Cryptographic Failures | ⚠️ Parcial | SECRET_KEY default; sem HTTPS configurado em dev |
| A03 | Injection | ✔️ OK | Django ORM protege contra SQL injection |
| A04 | Insecure Design | ⚠️ Parcial | Dados sensíveis enviados à OpenAI sem anonimização |
| A05 | Security Misconfiguration | ⚠️ Parcial | Portas expostas; CSP ausente; container como root |
| A06 | Vulnerable Components | ❌ Pendente | Sem auditoria automatizada de dependências |
| A07 | Auth Failures | ⚠️ Parcial | Sem rate limit no login |
| A08 | Data Integrity Failures | ✔️ OK | CSRF habilitado na maioria dos endpoints |
| A09 | Logging Failures | ⚠️ Parcial | Logging console-only, sem estrutura de SIEM |
| A10 | SSRF | ✔️ OK | Sem funcionalidade de fetch de URLs |

---

## 11. Prioridade de Correção

### 🔴 Correção Imediata (1 item)

| # | Achado | Esforço |
|---|--------|---------|
| 6.1 | CSRF desabilitado no GenerateSummaryView | 5 min |

### 🟠 Correção Alta Prioridade (5 itens)

| # | Achado | Esforço |
|---|--------|---------|
| 2.1 | Rate limit no login | 2h |
| 6.2 | Dados sensíveis enviados à OpenAI sem anonimização | 1-3 dias |
| 7.1 | PostgreSQL exposto (docker-compose) | 5 min |
| 7.2 | RabbitMQ exposto (docker-compose) | 5 min |
| 7.4 | Dockerfile roda como root | 30 min |

### 🟡 Correção Média Prioridade (6 itens)

| # | Achado | Esforço |
|---|--------|---------|
| 1.1 | SECRET_KEY com default inseguro | 5 min |
| 1.3 | CSP ausente | 1h |
| 5.1 | Validação de MIME type por header HTTP | 2h |
| 6.3 | Chave OpenAI sem criptografia em repouso | 2h (vault) |
| 7.3 | Redis sem autenticação | 15 min |
| 8.2 | Dependências não auditadas | 2h (CI) |

### 🟢 Baixa Prioridade (2 itens)

| # | Achado | Esforço |
|---|--------|---------|
| 3.1 | Timing attack (já mitigado) | 0 |
| 6.4 | Proteção anti-prompt-injection | 1-2 dias |

---

## 12. Resumo Geral

O sistema SCSI V1 na branch `sprint_29` apresenta uma base de segurança **sólida nos fundamentos**: RBAC por papel, isolamento multi-tenant via `TenantAwareModel`, document upload protegido, e uso do ORM Django (proteção contra SQL injection).

Os riscos mais significativos concentram-se em **três áreas**:

1. **AI Agent com dados sensíveis** — o envio de CPF, CNPJ, valores financeiros e sinistros para a API da OpenAI sem anonimização é o maior risco identificado. Isso requer contrato enterprise com garantia de no-training e, idealmente, pseudonimização dos dados antes do envio.

2. **Infraestrutura exposta** — o docker-compose.yml expõe PostgreSQL, RabbitMQ e Redis para o host. Embora isso seja comum em desenvolvimento, a configuração pode vazar para produção se não houver supervisão. O docker-stack.yml (Swarm) está correto.

3. **Falta de proteções perimetrais** — sem rate limit no login, sem CSP, sem auditoria de dependências, e uma única view com CSRF desabilitado.

14 achados identificados, sendo 1 crítico, 5 de alta severidade, 6 médios e 2 baixos. As correções imediatas e de alta prioridade somam aproximadamente 4-6 horas de trabalho.

---

*Relatório gerado por auditoria estática de código. Recomenda-se complementar com teste dinâmico (DAST) e varredura de dependências (`pip-audit`).*
