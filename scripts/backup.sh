#!/bin/bash
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/backups}"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

echo "[$(date)] Iniciando backup..."

DB_CONTAINER=$(docker ps -q -f name=scsi_db | head -n1)

if [ -z "$DB_CONTAINER" ]; then
    echo "ERRO: Container scsi_db não encontrado."
    exit 1
fi

echo "[$(date)] Backup do PostgreSQL..."
docker exec "$DB_CONTAINER" pg_dump -U "${POSTGRES_USER:-scsi}" "${POSTGRES_DB:-scsi}" | \
    gzip > "${BACKUP_DIR}/db_${DATE}.sql.gz"

echo "[$(date)] Backup da mídia..."
docker run --rm \
    -v scsi_media_data:/data:ro \
    -v "${BACKUP_DIR}:/backup" \
    alpine tar czf "/backup/media_${DATE}.tar.gz" -C /data .

echo "[$(date)] Rotação: removendo backups com mais de 30 dias..."
find "$BACKUP_DIR" -name "*.gz" -mtime +30 -delete 2>/dev/null || true

echo "[$(date)] Backup concluído: db_${DATE}.sql.gz e media_${DATE}.tar.gz"