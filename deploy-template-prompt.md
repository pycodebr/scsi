# CONTEXTO E PAPEL
Você é um engenheiro de plataforma especialista em Django + Docker Swarm. Eu
tenho um projeto Django **já existente** (o código está neste repositório) e
quero implementar nele uma arquitetura de deploy de produção em VPS, padronizada
e replicável — pense nela como um "template de deploy" que pode ser aplicado a
qualquer projeto Django. NÃO assuma nada sobre o projeto sem antes inspecionar o
código.

Parâmetros do meu deploy (use estes valores; se algum estiver vazio, pergunte ou
detecte a partir do projeto):
- Domínio: {{DOMINIO ex: meuapp.com}}
- Registry de imagens: {{REGISTRY ex: ghcr.io/usuario/projeto}}
- Nome do stack no Swarm: {{STACK_NAME ex: meuapp}}
- Provedor de DNS para TLS: Cloudflare (token de API com escopo DNS)
- Servidor: VPS Ubuntu, Docker Swarm single-node (deve poder escalar).



# ETAPA 1 — ANÁLISE DO PROJETO (faça antes de escrever qualquer coisa)
Inspecione o repositório e me devolva um diagnóstico curto cobrindo:
- Versões: Python, Django e libs relevantes (ler requirements/pyproject).
- Como o settings.py lê configuração (django-environ? os.environ? múltiplos
settings?) e onde estão ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, DATABASE, segurança.
- Banco de dados usado e como a URL/credenciais são montadas.
- Se há Celery/RabbitMQ/Redis, cache, e-mail, armazenamento de media/estáticos.
- O que já existe de deploy: Dockerfile, docker-compose, entrypoint, scripts,
CI/CD, healthcheck, settings de produção.
- Servidor WSGI/ASGI usado (gunicorn/uvicorn) e como o app é servido.
- Quaisquer particularidades (multi-tenant, middlewares, websockets, etc.).
Liste explicitamente o que **falta** para a arquitetura-alvo abaixo.



# ETAPA 2 — ARQUITETURA DE DEPLOY ALVO (TEMPLATE A SER IMPLEMENTADO)
Implemente (no PRD) a seguinte arquitetura, **adaptando** ao que o projeto
realmente usa. Componentes condicionais (Celery/RabbitMQ/Redis) só entram se o
projeto os utilizar; caso contrário, simplifique e justifique.

## Orquestração e serviços
- Docker + Docker Compose para rodar localmente; Docker Swarm para produção na
VPS, via `docker stack deploy`.
- Serviços típicos do stack: app web (Django), banco (PostgreSQL), Traefik como
reverse proxy/load balancer e, **se aplicável**: celery worker, celery beat,
rabbitmq (broker) e redis (result backend/cache).
- A imagem da aplicação publicada em um registry ({{REGISTRY}}); o deploy usa
`docker stack deploy --with-registry-auth`.
- Volumes nomeados para persistência (banco, redis, rabbitmq, media,
staticfiles e certificados do Let's Encrypt).
- Redes overlay: uma pública (`traefik_public`, external, compartilhada com o
Traefik) e uma interna isolada (`internal: true`) para os serviços de backend.

## TLS / Traefik / Cloudflare
- Traefik emitindo certificado TLS **wildcard** ({{DOMINIO}} e *.{{DOMINIO}})
via Let's Encrypt usando o desafio **DNS-01** com o provider Cloudflare
(obrigatório para wildcard; não combinar tlschallenge e dnschallenge no mesmo
resolver).
- É preciso um **token de API do Cloudflare** com escopo DNS (Zone > DNS > Edit)
na zona do domínio. O token nunca em texto puro: deve virar um **Docker Secret**
(`CLOUDFLARE_DNS_API_TOKEN`) e ser lido pelo Traefik via convenção de arquivo
`CF_DNS_API_TOKEN_FILE=/run/secrets/CLOUDFLARE_DNS_API_TOKEN`.
- Traefik deve redirecionar http→https e confiar nas faixas de IP do Cloudflare
(`forwardedHeaders.trustedIPs`). Dashboard protegido por Basic Auth (hash gerado
com `htpasswd -nbB`, com os `$` duplicados para `$$` no stack file).
- Se usar o healthcheck do load balancer do Traefik (`loadbalancer.healthcheck`)
com `ALLOWED_HOSTS` restrito, defina também
`loadbalancer.healthcheck.hostname={{DOMINIO}}`. Sem isso, o Traefik envia o IP
interno da task (ex.: 10.0.x.x) no header Host e o Django responde
400 DisallowedHost, marcando o backend como unhealthy. (O healthcheck do próprio
container, que bate em 127.0.0.1, não tem esse problema porque localhost está em
ALLOWED_HOSTS.)

## Configuração (.env e settings)
- Configuração via `.env` na raiz (gitignored). O `.env` de produção da VPS é
separado do de desenvolvimento. Os serviços recebem variáveis via `env_file`
(lido direto pelo Docker, sem shell). Scripts que leem o `.env` devem usar um
**parser seguro** de KEY=VALUE (nunca `source`/`.`), pois valores com `& $ * @`
quebram o shell.
- `ALLOWED_HOSTS` e `CSRF_TRUSTED_ORIGINS` lidos como **lista separada por
vírgula**. Padrão:
`ALLOWED_HOSTS={{DOMINIO}},.{{DOMINIO}},localhost,127.0.0.1` (o ponto inicial
cobre subdomínios; localhost/127.0.0.1 são **obrigatórios** para o healthcheck
interno passar). `CSRF_TRUSTED_ORIGINS=https://{{DOMINIO}},https://*.{{DOMINIO}}`
(sempre com esquema; suporte a wildcard). Em ALLOWED_HOSTS vai só o hostname.
- Em produção (DEBUG=False), como o TLS termina no Traefik e o app recebe HTTP
interno, configurar `SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO','https')`
(evita loop de redirect) e isentar a rota de healthcheck do redirect HTTPS com
`SECURE_REDIRECT_EXEMPT`. Habilitar HSTS, cookies seguros, nosniff, etc.
- Segredos sensíveis (senha de banco/broker, token Cloudflare) preferir Docker
Secrets e/ou o `.env` gitignored da VPS — nunca versionados.

## Saúde, ordem de subida e migrations
- Endpoint leve `/health/` no Django retornando 200, **sem** acessar banco e
**sem** exigir autenticação. Usado pelo HEALTHCHECK do container e pelo
healthcheck do load balancer do Traefik.
- Healthcheck em todos os serviços: app (HTTP em /health/), postgres
(`pg_isready`), redis (`redis-cli ping`), rabbitmq
(`rabbitmq-diagnostics check_port_connectivity`), com `start_period` adequado.
- O Swarm ignora `depends_on` em runtime: a ordem é garantida por healthchecks +
um django command `wait_for_db` usado nos entrypoints.
- Migrations seguras com múltiplas réplicas: o entrypoint do **app** aguarda o
banco, aplica migrations com **advisory lock** do PostgreSQL (só uma réplica
migra por vez) e roda collectstatic. Celery (worker/beat) usa um **entrypoint
separado** que só aguarda o banco e NÃO migra nem coleta estáticos.

## Resiliência e zero-downtime
- `restart_policy` em todos os serviços (condition on-failure, delay,
max_attempts, window) e `resource limits` (limits/reservations de CPU e memória)
para evitar starvation na VPS.
- `update_config` do app com `order: start-first` e `failure_action: rollback`
(sobe réplica nova saudável antes de derrubar a antiga; rollback automático se o
healthcheck falhar) + `rollback_config`.
- Servidor de aplicação com configuração de produção (ex.: gunicorn com
worker-class apropriada, `--max-requests` para reciclar workers, timeouts).

## Scripts
- `scripts/deploy.sh` (executado na própria VPS) que faz o ciclo completo:
carrega `.env` com parser seguro, valida pré-condições (Swarm ativo, secret do
Cloudflare, rede `traefik_public`, DEBUG=False e localhost em ALLOWED_HOSTS),
git pull, build e push da imagem para o registry, `docker stack deploy
--with-registry-auth` e rollout forçado dos serviços da aplicação; com modo
`--skip-build` para redeploy sem rebuild.
- `scripts/backup.sh` para backup do banco e da media, com rotação.



# ETAPA 3 — ENTREGÁVEL 1: PRD.md
Gere um arquivo **PRD.md** (Product Requirement Document) na raiz, em markdown,
contendo:
1. Visão geral e objetivo do trabalho de deploy.
2. Diagnóstico do estado atual do projeto (da Etapa 1) e gap analysis.
3. Decisões de arquitetura e quais componentes condicionais se aplicam a ESTE
projeto (com justificativa).
4. Especificação técnica detalhada de cada item da arquitetura-alvo, já
adaptada ao projeto (nomes de serviços, variáveis, arquivos a criar/alterar).
5. **Sprints de implementação** em ordem lógica, com tarefas pequenas e bem
detalhadas, cada uma como checklist `[ ]` para marcar `[x]` quando concluída.
Cada tarefa deve dizer o arquivo afetado e o critério de pronto. Sugestão de
ordenação: (S0) preparação e análise; (S1) Dockerfile + entrypoints +
wait_for_db; (S2) settings/.env (ALLOWED_HOSTS, CSRF, proxy SSL, health);
(S3) endpoint /health/; (S4) docker-compose local; (S5) docker-stack.yml com
healthchecks/restart/limits/secrets/redes/volumes; (S6) Traefik + Cloudflare
DNS-01 wildcard; (S7) scripts deploy.sh/backup.sh; (S8) validação e hardening.
6. Riscos e pontos de atenção (ex.: arquitetura de build amd64 vs ARM, perda de
dados em volumes, rotação de segredos).

Regras: não quebre funcionalidades existentes; mudanças idempotentes; mantenha o
padrão de código do projeto; não exponha segredos; use placeholders onde o valor
for específico do ambiente.



# ETAPA 4 — ENTREGÁVEL 2: GUIA DE DEPLOY PASSO A PASSO
Inclua no PRD (ou em `docs/deploy.md`, se o projeto usar MkDocs) um **guia
completo de deploy do zero numa VPS Ubuntu**, com cada comando em blocos
copiáveis e explicação curta de cada passo, cobrindo no mínimo:
1. Provisionar a VPS: usuário não-root, atualização, firewall, instalação do
Docker Engine + Compose plugin.
2. `docker swarm init` e criação das redes overlay (traefik_public external +
rede interna).
3. Apontar o DNS no Cloudflare (A/AAAA + wildcard) e criar o **token de API**
com escopo DNS na zona do domínio; criar o **Docker Secret**
`CLOUDFLARE_DNS_API_TOKEN`.
4. Criar o `.env` de produção (DEBUG=False, ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS
no padrão definido, banco, e-mail, etc.) e os demais secrets necessários.
5. Login no registry e primeiro `docker stack deploy --with-registry-auth` (ou
`./scripts/deploy.sh`).
6. Verificar emissão do certificado wildcard via DNS-01 (logs do Traefik) e o
healthcheck dos serviços ficando `healthy`.
7. Operação do dia a dia: redeploy/atualização, ver logs, rollout, criar
superusuário, rodar comandos no container, e troubleshooting comum:
   - `DisallowedHost` por falta de `localhost`/`127.0.0.1` em ALLOWED_HOSTS (o
   healthcheck do container falha).
   - Backend marcado unhealthy + `400` de `Go-http-client` em `/health/` por
   falta de `loadbalancer.healthcheck.hostname` no Traefik quando ALLOWED_HOSTS
   é restrito (Traefik manda o IP da task como Host).
   - Loop de redirect HTTPS por falta de `SECURE_PROXY_SSL_HEADER` atrás do
   proxy.
   - `ACCESS_REFUSED` no broker por credencial divergente / RabbitMQ recriado.
   - Certificado não emitido por token/secret do Cloudflare errado ou por usar
   tlschallenge junto do dnschallenge.
   - `failed to resolve host 'db'` / tabela inexistente durante a subida —
   resolvido por healthchecks + wait_for_db (transitório).
8. Backup/restore e rotação de segredos.



# FORMATO DA RESPOSTA
Primeiro mostre o diagnóstico da Etapa 1. Em seguida, crie/atualize os arquivos
(PRD.md e, se aplicável, docs/deploy.md). Não comece a implementar o código do
deploy ainda — o objetivo desta tarefa é entregar o PRD com as sprints e o guia.
Ao final, liste os arquivos criados e um resumo do plano.
