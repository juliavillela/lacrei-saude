#!/bin/sh
set -e

if [ "$1" = "gunicorn" ]; then
    echo "Applying migrations..."
    python manage.py migrate --noinput
    echo "Starting Gunicorn..."
    exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
else
    exec "$@"
fi