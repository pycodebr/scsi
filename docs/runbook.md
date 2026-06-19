# Runbook — Operação e Monitoramento

## Serviços e health checks

| Serviço | Porta | Health check | Comando |
|---|---|---|---|
| Traefik | 80/443 | `curl -s http://localhost:8080/ping` | `docker service logs -f scsi_traefik` |
| Django App | 8000 | `curl -s http://localhost:8000/admin/` | `docker service logs -f scsi_app` |
| PostgreSQL | 5432 | `pg_isready -U scsi` | `docker service logs -f scsi_db` |
| RabbitMQ | 5672/15672 | `curl -s http://localhost:15672/` | `docker service logs -f scsi_rabbitmq` |
| Redis | 6379 | `redis-cli ping` | `docker service logs -f scsi_redis` |
| Celery Worker | — | Ver filas no RabbitMQ Management | `docker service logs -f scsi_celery_worker` |
| Celery Beat | — | Ver tasks agendadas no Admin | `docker service logs -f scsi_celery_beat` |

## Alertas comuns

### App não responde (502/503)

1. Verificar se o serviço está rodando: `docker service ls`
2. Verificar logs: `docker service logs scsi_app --tail 100`
3. Restart: `docker service update --force scsi_app`

### Celery worker travado

1. Verificar filas no RabbitMQ Management (http://server:15672)
2. Verificar logs: `docker service logs scsi_celery_worker --tail 100`
3. Restart: `docker service update --force scsi_celery_worker`

### Banco de dados lento

1. Verificar conexões: `docker exec -it $(docker ps -q -f name=scsi_db) psql -U scsi -c "SELECT count(*) FROM pg_stat_activity;"`
2. Verificar queries lentas: `docker exec -it $(... ) psql -U scsi -c "SELECT query, duration FROM pg_stat_activity WHERE state='active';"`
3. Verificar volume: `docker system df`

### SSL expirado ou não renovado

1. Verificar logs do Traefik: `docker service logs scsi_traefik | grep -i acme`
2. Verificar volume `letsencrypt`: `docker volume inspect scsi_letsencrypt`
3. Forçar renovação: restartar Traefik com `docker service update --force scsi_traefik`

## Procedimentos

### Scaling manual

```bash
# Escalar workers para 4 réplicas
docker service scale scsi_celery_worker=4

# Reduzir para 2
docker service scale scsi_celery_worker=2
```

### Deploy de nova versão

```bash
docker build -t ghcr.io/pycodebr/scsi:latest .
docker push ghcr.io/pycodebr/scsi:latest
docker service update --image ghcr.io/pycodebr/scsi:latest scsi_app
docker service update --image ghcr.io/pycodebr/scsi:latest scsi_celery_worker
```

### Migração em produção

```bash
APP=$(docker ps --filter name=scsi_app -q | head -n1)
docker exec -it $APP python manage.py migrate
```

### Rollback

```bash
# Se a nova versão causou problemas
docker service rollback scsi_app
docker service rollback scsi_celery_worker
```

## Logs

| Fonte | Comando | Destino sugerido |
|---|---|---|
| App | `docker service logs scsi_app` | stdout + arquivo |
| Worker | `docker service logs scsi_celery_worker` | stdout + arquivo |
| Traefik | `docker service logs scsi_traefik` | stdout + arquivo |
| DB | `docker service logs scsi_db` | stdout + arquivo |

Para produção, configurar Docker logging driver para envio a centralização (ex.: Loki, ELK, ou CloudWatch).

## Monitoramento

- **Celery:** Admin em `/admin/celery/` (dj-celery-panel)
- **RabbitMQ:** Management UI em `http://server:15672`
- **PostgreSQL:** `pg_stat_activity`, `pg_stat_statements`
- **Redis:** `redis-cli info`

### Métricas sugeridas (futuro)

- Prometheus + Grafana
- Django metrics via `django-prometheus`
- Celery metrics via `flower`
- PostgreSQL metrics via `postgres_exporter`