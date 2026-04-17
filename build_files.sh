#!/bin/bash
set -e

pip install -r requirements.txt -q
python manage.py collectstatic --noinput
