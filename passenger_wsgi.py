"""Точка входа WSGI для Phusion Passenger (хостинг Hostland).

Passenger запускает этот файл и ищет в нём объект `application`.
Скрипт добавляет в sys.path папку проекта и site-packages локального venv,
чтобы Django и зависимости находились независимо от того, какой
интерпретатор выбран в Passenger.
"""

import glob
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# venv проекта: venv/lib/python3.*/site-packages
_venv_site_packages = glob.glob(
    os.path.join(BASE_DIR, "venv", "lib", "python3.*", "site-packages")
)
for _path in _venv_site_packages:
    if _path not in sys.path:
        sys.path.insert(0, _path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from config.wsgi import application  # noqa: E402  (импорт после настройки путей)