#!/bin/bash
set -e

# Переменные окружения передаются извне.
# Пример: DB_PASSWORD=... ALLOWED_HOSTS=10.0.0.5 deploy/setup_env.sh
cd /opt/services_journal

DB_PASSWORD="${DB_PASSWORD:?Укажите DB_PASSWORD}"
ALLOWED_HOSTS="${ALLOWED_HOSTS:?Укажите ALLOWED_HOSTS}"

SECRET_KEY="$(./venv/bin/python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"

cat > .env <<EOF
SECRET_KEY=${SECRET_KEY}
DEBUG=False
ALLOWED_HOSTS=${ALLOWED_HOSTS}

DB_NAME=services_journal
DB_USER=services_journal
DB_PASSWORD=${DB_PASSWORD}
DB_HOST=localhost
DB_PORT=5432
EOF

echo "ENV_WRITTEN"