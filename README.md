# Журнал регистрации услуг

Веб-приложение на Django для ведения журнала оказания услуг: клиенты, справочник услуг,
записи журнала с составом оказанных услуг и печать бланка заказа в PDF.

## Стек

- Python 3, Django 5
- PostgreSQL
- Gunicorn + Nginx (на сервере)
- WeasyPrint (генерация PDF)

## Структура

```
services_journal/
├── manage.py
├── requirements.txt
├── .env.example
├── config/          # настройки, urls, wsgi/asgi
├── apps/
│   ├── accounts/    # вход и роли (admin/operator)
│   ├── clients/     # клиенты
│   ├── services/    # справочник услуг
│   ├── journal/     # журнал регистрации услуг
│   └── reports/     # PDF бланк заказа
├── templates/
├── static/
└── deploy/          # gunicorn.service, nginx.conf, deploy.sh
```

## Локальный запуск (Windows, для разработки)

Требуется PostgreSQL (локально или на сервере в VirtualBox).

```bat
cd C:\Users\tr777\PythonProjects\services_journal
python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt

copy .env.example .env
:: заполнить .env (DB_*)

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Открыть http://127.0.0.1:8000/

> Для разработки на Windows без локального PostgreSQL можно временно переключить
> `DATABASES` в `config/settings.py` на SQLite, но для прод-совместимости используйте PostgreSQL.

## Роли

При выполнении `migrate` автоматически создаются группы:

- `admin` — администратор (добавьте пользователя в эту группу и/или дайте права staff)
- `operator` — оператор

Доступ в `/admin/` имеют пользователи с флагом `is_staff` (задаётся через `createsuperuser`
или в админке).

## Деплой на Ubuntu Server (VirtualBox)

Полные команды и пояснения — в файле `deploy/README.md`.

Кратко:

```bash
# 1. пакеты и PostgreSQL
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip git nginx postgresql postgresql-contrib
sudo apt install -y python3-dev libpq-dev build-essential
sudo apt install -y libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-2.0-0 libffi-dev shared-mime-info libcairo2 libharfbuzz0b libpangoft2-1.0-0 fonts-dejavu fonts-liberation

# 2. база
sudo -u postgres psql -c "CREATE USER services_journal WITH PASSWORD 'change_me';"
sudo -u postgres psql -c "CREATE DATABASE services_journal OWNER services_journal;"

# 3. проект
sudo mkdir -p /opt/services_journal
sudo chown $USER:$USER /opt/services_journal
git clone <repo> /opt/services_journal
cd /opt/services_journal
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # заполнить SECRET_KEY, DEBUG=False, ALLOWED_HOSTS, DB_*

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser

# 4. systemd + nginx
sudo cp deploy/gunicorn.service /etc/systemd/system/gunicorn.service
sudo cp deploy/nginx.conf /etc/nginx/sites-available/services_journal
sudo ln -s /etc/nginx/sites-available/services_journal /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo systemctl daemon-reload
sudo systemctl enable --now gunicorn
sudo nginx -t
sudo systemctl reload nginx
```

## Основные URL

- `/` — редирект на журнал
- `/journal/` — журнал регистрации услуг
- `/clients/` — клиенты
- `/services/` — справочник услуг
- `/reports/order/<id>/pdf/` — PDF бланк заказа
- `/admin/` — админка Django