#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate --noinput || true

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear || true

echo "Starting Gunicorn..."
exec gunicorn config.asgi:application --bind :8000 -k uvicorn.workers.UvicornWorker