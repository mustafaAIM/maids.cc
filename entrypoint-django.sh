#!/bin/bash
echo "Starting Django running..."

run_migrations() {
    app_name=$1
    echo "Running migrations for $app_name..."
    python manage.py makemigrations $app_name --noinput || exit 1
    python manage.py migrate $app_name --noinput || exit 1
    return 0
}

python manage.py makemigrations --noinput
python manage.py migrate --noinput

run_migrations "authentication"
run_migrations "books"
run_migrations "patrons"
run_migrations "borrowings"

gunicorn maids.wsgi:application \
    --bind 0.0.0.0:8000 \
    