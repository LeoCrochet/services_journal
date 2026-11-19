#!/usr/bin/env bash
# Развёртывание проекта на shared-хостинге Hostland (Passenger 6 + Apache + MySQL).
# Запускать на сервере:
#   SECRET_KEY="..." DB_PASSWORD="..." SUPERUSER_PASSWORD="..." bash deploy_hostland.sh
#
# Скрипт идемпотентный: повторный запуск обновляет код и применяет миграции.

set -euo pipefail

# ----------------------------- настройки -----------------------------------
DOMAIN="domain1328304.ru.host1328304.serv7.hostland.pro"
PROJECT_DIR="$HOME/$DOMAIN"
REPO_URL="https://github.com/LeoCrochet/services_journal.git"
BRANCH="develop"
PYTHON="/usr/bin/python3.12"

DB_NAME="host1328304_journal"
DB_USER="host1328304_root8"
DB_HOST="127.0.0.1"
DB_PORT="3308"
DB_PASSWORD="${DB_PASSWORD:?Задайте DB_PASSWORD в окружении перед запуском}"
SECRET_KEY="${SECRET_KEY:?Задайте SECRET_KEY в окружении перед запуском}"

SUPERUSER_NAME="${SUPERUSER_NAME:-admin}"
SUPERUSER_EMAIL="${SUPERUSER_EMAIL:-admin@example.com}"
SUPERUSER_PASSWORD="${SUPERUSER_PASSWORD:-}"

# ----------------------------- код проекта ---------------------------------
if [ -d "$PROJECT_DIR/.git" ]; then
  echo "==> Обновление кода в $PROJECT_DIR"
  git -C "$PROJECT_DIR" fetch origin "$BRANCH"
  git -C "$PROJECT_DIR" checkout "$BRANCH"
  git -C "$PROJECT_DIR" pull --ff-only origin "$BRANCH"
else
  if [ -d "$PROJECT_DIR" ] && [ -n "$(ls -A "$PROJECT_DIR" 2>/dev/null)" ]; then
    BACKUP_DIR="$HOME/_backup_${DOMAIN}_$(date +%Y%m%d_%H%M%S)"
    echo "==> Папка домена не пуста, переношу содержимое в $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"
    mv "$PROJECT_DIR"/* "$PROJECT_DIR"/.[!.]* "$PROJECT_DIR"/..?* "$BACKUP_DIR"/ 2>/dev/null || true
  fi
  echo "==> Клонирование ветки $BRANCH в $PROJECT_DIR"
  git clone --branch "$BRANCH" "$REPO_URL" "$PROJECT_DIR"
fi

cd "$PROJECT_DIR"

# ----------------------------- виртуальное окружение -----------------------
if [ ! -x "$PROJECT_DIR/venv/bin/python" ]; then
  echo "==> Создание venv ($PYTHON)"
  "$PYTHON" -m venv "$PROJECT_DIR/venv"
fi

echo "==> Установка зависимостей"
"$PROJECT_DIR/venv/bin/python" -m pip install --upgrade pip wheel
"$PROJECT_DIR/venv/bin/python" -m pip install -r requirements-hostland.txt

# ----------------------------- .env ----------------------------------------
echo "==> Запись .env"
umask 077
{
  echo "SECRET_KEY=$SECRET_KEY"
  echo "DEBUG=False"
  echo "ALLOWED_HOSTS=$DOMAIN,localhost,127.0.0.1"
  echo "CSRF_TRUSTED_ORIGINS=https://$DOMAIN"
  echo ""
  echo "DB_ENGINE=django.db.backends.mysql"
  echo "DB_NAME=$DB_NAME"
  echo "DB_USER=$DB_USER"
  echo "DB_PASSWORD=$DB_PASSWORD"
  echo "DB_HOST=$DB_HOST"
  echo "DB_PORT=$DB_PORT"
} > "$PROJECT_DIR/.env"

# ----------------------------- Passenger -----------------------------------
echo "==> Настройка .htaccess для Passenger"
{
  echo "PassengerAppRoot $PROJECT_DIR"
  echo "PassengerBaseURI /"
  echo "PassengerAppType wsgi"
  echo "PassengerStartupFile passenger_wsgi.py"
  echo "PassengerPython $PYTHON"
  echo "PassengerAppEnv production"
} > "$PROJECT_DIR/.htaccess"

mkdir -p "$PROJECT_DIR/tmp"
touch "$PROJECT_DIR/tmp/restart.txt"

# ----------------------------- миграции и статика --------------------------
echo "==> Миграции"
"$PROJECT_DIR/venv/bin/python" manage.py migrate --noinput

echo "==> Сбор статики"
"$PROJECT_DIR/venv/bin/python" manage.py collectstatic --noinput

echo "==> Проверка конфигурации Django"
"$PROJECT_DIR/venv/bin/python" manage.py check

# ----------------------------- суперпользователь ---------------------------
if [ -n "$SUPERUSER_PASSWORD" ]; then
  echo "==> Создание/обновление суперпользователя $SUPERUSER_NAME"
  DJANGO_SUPERUSER_PASSWORD="$SUPERUSER_PASSWORD" \
  "$PROJECT_DIR/venv/bin/python" manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
user, created = User.objects.get_or_create(
    username='$SUPERUSER_NAME',
    defaults={'email': '$SUPERUSER_EMAIL'},
)
user.is_staff = True
user.is_superuser = True
user.email = '$SUPERUSER_EMAIL'
user.set_password('$SUPERUSER_PASSWORD')
user.save()
print('created' if created else 'updated', user.username)
"
fi

# Перезапуск приложения
touch "$PROJECT_DIR/tmp/restart.txt"

echo "==> Готово: https://$DOMAIN/"