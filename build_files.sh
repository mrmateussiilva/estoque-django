#!/bin/bash
set -e

pip install -r requirements.txt -q --break-system-packages
python manage.py migrate --noinput
python manage.py collectstatic --noinput
