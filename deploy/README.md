# Деплой на Ubuntu Server (VirtualBox)

## 1. Системные пакеты

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip git nginx postgresql postgresql-contrib
sudo apt install -y python3-dev libpq-dev build-essential
sudo apt install -y libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-2.0-0 \
  libffi-dev shared-mime-info libcairo2 libharfbuzz0b libpangoft2-1.0-0 \
  fonts-dejavu fonts-liberation
```

## 2. База данных PostgreSQL

```bash
sudo -u postgres psql <<'SQL'
CREATE USER services_journal WITH PASSWORD 'change_me';
CREATE DATABASE services_journal OWNER services_journal;
SQL
```

## 3. Код приложения

```bash
sudo mkdir -p /opt/services_journal
sudo chown $USER:$USER /opt/services_journal
git clone <URL_репозитория> /opt/services_journal
cd /opt/services_journal

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Переменные окружения

```bash
cp .env.example .env
nano .env
```

Обязательные значения:

```
SECRET_KEY=сгенерированный_ключ
DEBUG=False
ALLOWED_HOSTS=IP_сервера,домен
DB_NAME=services_journal
DB_USER=services_journal
DB_PASSWORD=change_me
DB_HOST=localhost
DB_PORT=5432
```

Сгенерировать SECRET_KEY:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 5. Миграции и статика

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## 6. Gunicorn как systemd-сервис

```bash
sudo cp deploy/gunicorn.service /etc/systemd/system/gunicorn.service
sudo systemctl daemon-reload
sudo systemctl enable --now gunicorn
sudo systemctl status gunicorn
```

Проверить логи:

```bash
sudo journalctl -u gunicorn -f
```

## 7. Nginx

```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/services_journal
sudo sed -i 's/SERVER_IP/IP_СЕРВЕРА/' /etc/nginx/sites-available/services_journal
sudo ln -s /etc/nginx/sites-available/services_journal /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl enable --now nginx
sudo systemctl reload nginx
```

## 8. Обновление после изменений в коде

```bash
cd /opt/services_journal
source venv/bin/activate
git pull
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn