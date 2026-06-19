# Backup e Restore

## Estratégia

O SCSI usa **backup lógico** (`pg_dump`) para o banco e **snapshot de volume** para arquivos de mídia.

## Backup automático

### Script de backup (`scripts/backup.sh`)

```bash
#!/bin/bash
set -euo pipefail

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup do PostgreSQL
docker exec $(docker ps -q -f name=scsi_db) \
  pg_dump -U scsi scsi | gzip > "${BACKUP_DIR}/db_${DATE}.sql.gz"

# Backup da mídia
docker run --rm -v scsi_media_data:/data -v ${BACKUP_DIR}:/backup \
  alpine tar czf /backup/media_${DATE}.tar.gz -C /data .

echo "Backup concluído: db_${DATE}.sql.gz e media_${DATE}.tar.gz"
```

### Cron de backup

```bash
# Rodar diariamente às 3h (no host)
0 3 * * * /home/deploy/scsi/scripts/backup.sh >> /var/log/scsi-backup.log 2>&1
```

### Rotação (manter 30 dias)

```bash
find /backups -name "*.gz" -mtime +30 -delete
```

## Restore

### Restaurar banco

```bash
# Parar o app para evitar escrita durante restore
docker service scale scsi_app=0 scsi_celery_worker=0

# Restaurar PostgreSQL
gunzip -c /backups/db_20260101_030000.sql.gz | \
  docker exec -i $(docker ps -q -f name=scsi_db) \
  psql -U scsi scsi

# Reiniciar serviços
docker service scale scsi_app=1 scsi_celery_worker=2
```

### Restaurar mídia

```bash
docker run --rm -v scsi_media_data:/data -v /backups:/backup \
  alpine tar xzf /backup/media_20260101_030000.tar.gz -C /data
```

## Off-site

Para segurança adicional, enviar backups para armazenamento externo:

- **S3-compatible:** `aws s3 cp /backups/ s3://scsi-backups/ --recursive`
- **Rsync:** `rsync -avz /backups/ backup-server:/backups/scsi/`

## Checklist de restore

1. Confirmar backup existe e não está corrompido (`gunzip -t`)
2. Parar serviços de escrita (app + worker)
3. Restaurar banco
4. Restaurar mídia
5. Reiniciar serviços
6. Validar: acessar app, verificar dados e arquivos