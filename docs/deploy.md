# Deploy com Docker Swarm + Traefik

> Guia passo a passo para deploy em VPS Ubuntu 22.04/24.04 LTS. Domínio exemplo: `scsi.digital`.

## Visão geral da infraestrutura

```mermaid
graph TB
    Internet[Internet] --> Traefik[Traefik<br/>Port 80/443<br/>SSL Let's Encrypt]
    Traefik --> App[Django App<br/>Gunicorn]
    App --> DB[(PostgreSQL 16)]
    App --> RabbitMQ[RabbitMQ]
    App --> Redis[(Redis)]
    App --> Media[/media volume<br/>arquivos protegidos]
    Worker[Celery Worker x2] --> DB
    Worker --> RabbitMQ
    Worker --> Redis
    Beat[Celery Beat] --> DB
    Beat --> RabbitMQ

    subgraph Docker Swarm
        Traefik
        App
        Worker
        Beat
        DB
        RabbitMQ
        Redis
    end
```

## Pré-requisitos

- VPS Ubuntu 22.04/24.04 LTS
- Domínio apontando para o IP da VPS
- Docker instalado na VPS
- Acesso SSH

## Passo a passo

### 1. Atualizar o servidor e criar usuário

```bash
ssh root@SEU_IP
apt update && apt upgrade -y
adduser deploy
usermod -aG sudo deploy
# Configurar chave SSH para deploy e desabilitar login root/senha
```

### 2. Firewall

```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### 3. Instalar Docker

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
usermod -aG docker deploy
```

### 4. Inicializar Docker Swarm

```bash
docker swarm init --advertise-addr SEU_IP
docker node ls
```

### 5. Criar rede overlay do Traefik

```bash
docker network create --driver overlay --attachable traefik_public
```

### 6. Configurar DNS

No Cloudflare (ou outro DNS):
1. Registro A: `scsi.digital` → `SEU_IP`
2. Registro A/CNAME: `www` → `scsi.digital` (ou `SEU_IP`)
3. SSL/TLS → modo **Full (strict)**
4. Para a primeira emissão do certificado, deixar o registro como **DNS-only** (nuvem cinza)

### 7. Variáveis de ambiente

```bash
# Na VPS, diretório do projeto (ex.: /home/deploy/scsi)
cp .env.example .env
nano .env   # Preencher SECRET_KEY, DB, RabbitMQ, OPENAI_API_KEY, ACME_EMAIL, etc.
```

### 8. Build e push da imagem

```bash
docker login registry.example.com
docker build -t ghcr.io/pycodebr/scsi:latest .
docker push ghcr.io/pycodebr/scsi:latest
```

Ou usar o script de deploy:

```bash
./scripts/deploy.sh build
```

### 9. Deploy da stack

```bash
docker stack deploy -c docker-stack.yml scsi
docker stack services scsi
docker service ls
```

Ou com o script:

```bash
./scripts/deploy.sh
```

### 9. Criar docker-stack.yml

O arquivo `docker-stack.yml` na raiz do projeto contém a definição de todos os serviços:

- `traefik` — reverse proxy com SSL automático (Let's Encrypt)
- `app` — Django com Gunicorn
- `db` — PostgreSQL 16
- `rabbitmq` — broker Celery
- `redis` — cache e result backend
- `celery_worker` — worker (2 réplicas)
- `celery_beat` — scheduler

Volumes persistentes: `pg_data`, `media_data`, `static_data`, `letsencrypt`.

### 10. Deploy

```bash
docker stack deploy -c docker-stack.yml scsi
docker stack services scsi
docker service ls
```

### 11. Migrações, estáticos e superusuário

```bash
APP=$(docker ps --filter name=scsi_app -q | head -n1)
docker exec -it $APP python manage.py migrate
docker exec -it $APP python manage.py collectstatic --noinput
docker exec -it $APP python manage.py createsuperuser
```

> Alternativa: colocar `migrate` e `collectstatic` no `entrypoint.sh`.

### 12. Verificações

```bash
# Logs do Traefik (emissão de certificado SSL)
docker service logs -f scsi_traefik

# Acessar https://scsi.digital e validar cadeado (Let's Encrypt)

# Conferir volumes persistentes
docker volume ls | grep scsi
```

## Atualização (rolling update)

```bash
docker build -t ghcr.io/pycodebr/scsi:latest .
docker push ghcr.io/pycodebr/scsi:latest
docker service update --image ghcr.io/pycodebr/scsi:latest scsi_app
docker service update --image ghcr.io/pycodebr/scsi:latest scsi_celery_worker
```

## Observações de produção

- **SSL:** emitido automaticamente pelo Traefik (Let's Encrypt, `tlschallenge`). Cloudflare em **Full (strict)**.
- **Proxy/portas:** apenas Traefik expõe 80/443; demais serviços na rede `internal`.
- **Volumes:** `pg_data` (banco), `media_data` (anexos), `static_data` (estáticos), `letsencrypt` (certs) — todos persistentes.
- **Backups/logs:** ver [Backup e Restore](backup.md) e [Runbook](runbook.md).