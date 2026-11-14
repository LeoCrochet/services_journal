#!/bin/bash
set -e

# Бэкап PostgreSQL в /opt/services_journal/backups.
# Запускать по cron, например: ежедневно в 02:00
# 0 2 * * * /opt/services_journal/deploy/backup_db.sh >> /var/log/services_journal_backup.log 2>&1
BACKUP_DIR="${BACKUP_DIR:-/opt/services_journal/backups}"
DB_PASSWORD="${DB_PASSWORD:?Укажите DB_PASSWORD}"
KEEP_DAYS="${KEEP_DAYS:-30}"

mkdir -p "$BACKUP_DIR"

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
FILENAME="services_journal_${TIMESTAMP}.dump"

PGPASSWORD="$DB_PASSWORD" pg_dump \
    -h localhost \
    -U services_journal \
    -d services_journal \
    -F c \
    -f "$BACKUP_DIR/$FILENAME"

# Удаляем бэкапы старше KEEP_DAYS
find "$BACKUP_DIR" -name 'services_journal_*.dump' -mtime +"$KEEP_DAYS" -delete

echo "BACKUP_CREATED: $BACKUP_DIR/$FILENAME"