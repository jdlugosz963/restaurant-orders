#!/bin/sh

set -e

python manage.py collectstatic --noinput
python manage.py makemigrations --noinput
python manage.py migrate --noinput

daphne -b 0.0.0.0 -p 8000 restaurant_orders.asgi:application
