#!/bin/sh
set -e

echo "Waiting for database..."
until python -c "
import socket
import sys

try:
    socket.create_connection(('${DB_HOST:-db}', ${DB_PORT:-5432}), timeout=2)
except OSError:
    sys.exit(1)
"; do
    echo "Database is unavailable - sleeping"
    sleep 1
done
echo "Database is up!"

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting gunicorn on port ${PORT:-8000}..."
exec gunicorn core.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers 3 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile - \
    --log-level debug \
    --capture-output