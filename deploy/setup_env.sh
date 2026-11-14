#!/bin/bash
set -e

cd /opt/services_journal

SECRET_KEY="$(./venv/bin/python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"

cat > .env <<EOF
SECRET_KEY=${SECRET_KEY}
DEBUG=False
ALLOWED_HOSTS=10.240.7.52,127.0.0.1,localhost

DB_NAME=services_journal
DB_USER=services_journal
DB_PASSWORD=SjDb_2026_pw_Tr777
DB_HOST=localhost
DB_PORT=5432
EOF

echo "ENV_WRITTEN"