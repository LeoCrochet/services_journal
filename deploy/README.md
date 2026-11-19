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
```

## 9. Демо-стенд на Hostland (shared-хостинг, Passenger)

Демо живёт на ветке `deploy/hostland` — ветка `develop` остаётся «чистой».

Пути на сервере:

- каталог приложения (Passenger app root): `~/domain1328304.ru/projects/journal`
- домен: `domain1328304.ru` (+ техдомен `domain1328304.ru.host1328304.serv7.hostland.pro`)
- БД: MySQL 8.0.45, `127.0.0.1:3308`, `host1328304_journal`

### Обновление демо после изменений в `develop`

```bash
# 1. Локально: перенести коммиты из develop в ветку деплоя
git checkout deploy/hostland
git cherry-pick <хеш_коммита>        # при конфликте правим и «git cherry-pick --continue»
git push origin deploy/hostland

# 2. На сервере (WebSSH)
cd ~/domain1328304.ru/projects/journal
git pull origin deploy/hostland
venv/bin/python manage.py migrate --noinput
venv/bin/python manage.py collectstatic --noinput
touch tmp/restart.txt                # перезапуск Passenger
```

Проверка:

```bash
curl -s -o /dev/null -w "root=%{http_code}\n" http://domain1328304.ru.host1328304.serv7.hostland.pro/
curl -s -o /dev/null -w "css=%{http_code}\n"  http://domain1328304.ru.host1328304.serv7.hostland.pro/assets/css/styles.css
```

### Особенности Hostland, из-за которых всё сделано именно так

1. **Статика — по `/assets/`, а не `/static/`.** nginx хостинга сам обрабатывает
   `/static/` и отдаёт свой 404, не передавая запрос в Passenger. Поэтому в
   `config/settings.py` на этой ветке `STATIC_URL = "/assets/"`, а раздачей
   занимается WhiteNoise. Шаблоны используют `{% static %}`, так что менять их
   не нужно.
2. **`tmp/` создаёт панель от root.** Тогда `touch tmp/restart.txt` падает с
   `Permission denied`. Лечится переименованием:
   `mv tmp tmp_root_old && mkdir -p tmp && touch tmp/restart.txt`.
3. **PDF (WeasyPrint).** На shared-хостинге нет системных библиотек pango/cairo,
   поэтому `weasyprint` может не импортироваться. `apps/reports/views.py` в этом
   случае отдаёт HTML-версию документа с плашкой и автопечатью (`window.print()`),
   откуда PDF сохраняется через Ctrl+P. DOCX и Excel работают всегда.
4. **Не нажимать «Сохранить» в окне Python в панели Hostland** — оно
   перезаписывает каталог приложения шаблонным проектом. Обновление кода — только
   через `git pull` + `touch tmp/restart.txt`.
5. **venv принадлежит root-у частично**: `venv/bin/pip` может быть недоступен
   (`Permission denied`). Ставить пакеты так:
   `venv/bin/python -m pip install <пакет>`.
