#!/bin/sh -e

set -e


# if [ "$DATABASE" = "postgres" ]; then
#     echo "Waiting for postgres..."

#     while ! nc -z "$POSTGRES_HOSTNAME" "$POSTGRES_PORT"; do
#       sleep 0.1
#     done

#     echo "PostgreSQL started"
# fi

echo "🛠️ Running migrations..."
uv run python manage.py migrate
# print("Iyanuoluwa")

echo "🚀 Starting server..."
uv run gunicorn config.wsgi:application --bind 0.0.0.0:8000

exec "$@"
