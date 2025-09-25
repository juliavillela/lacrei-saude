#!/bin/sh
set -e
PORT="${PORT:-8000}"

if [ "$1" = "gunicorn" ]; then
    echo "Applying migrations..."
    python manage.py migrate --noinput
    echo "Starting Gunicorn on 0.0.0.0:$PORT..."
    exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 3
else
    exec "$@"
fi