#!/bin/bash
set -e

# Пароли передаются через переменные окружения или аргументы.
# Пример: SUDO_PASSWORD=... DB_PASSWORD=... deploy/setup_db.sh
cd /opt/services_journal

SUDO_PASSWORD="${SUDO_PASSWORD:?Укажите SUDO_PASSWORD}"
DB_PASSWORD="${DB_PASSWORD:?Укажите DB_PASSWORD}"

# 1. Создать роль, если её нет
echo "$SUDO_PASSWORD" | sudo -S -u postgres psql \
    -v db_password="$DB_PASSWORD" \
    -f /opt/services_journal/deploy/setup_db.sql

# 2. Создать базу, если её нет
DB_EXISTS=$(echo "$SUDO_PASSWORD" | sudo -S -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname = 'services_journal'")
if [ "$DB_EXISTS" != "1" ]; then
    echo "$SUDO_PASSWORD" | sudo -S -u postgres createdb -O services_journal services_journal
fi

echo "DB_READY"