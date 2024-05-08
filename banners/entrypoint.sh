#!/usr/bin/env sh

echo "Apply database migrations"
python manage.py migrate

exec "$@"