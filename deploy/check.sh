#!/bin/bash

echo "== HTTP через localhost =="
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1/

echo "== HTTP через IP 10.240.7.52 =="
curl -s -o /dev/null -w "%{http_code}\n" http://10.240.7.52/

echo "== Заголовок логина (первые 200 байт) =="
curl -s http://127.0.0.1/accounts/login/ | head -c 200

echo ""
echo "== Статус gunicorn =="
echo Adad47pv | sudo -S systemctl is-active gunicorn

echo "== Статус nginx =="
echo Adad47pv | sudo -S systemctl is-active nginx

echo "== Проверка WeasyPrint/GTK =="
cd /opt/services_journal
./venv/bin/python -c "import weasyprint; print('WEASY_OK', weasyprint.__version__)"