#!/bin/bash
set -e

cd /opt/services_journal

# 1. Создать роль, если её нет
echo Adad47pv | sudo -S -u postgres psql -f /opt/services_journal/deploy/setup_db.sql

# 2. Создать базу, если её нет
DB_EXISTS=$(echo Adad47pv | sudo -S -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname = 'services_journal'")
if [ "$DB_EXISTS" != "1" ]; then
    echo Adad47pv | sudo -S -u postgres createdb -O services_journal services_journal
fi

echo "DB_READY"