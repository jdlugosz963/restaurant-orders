#!/bin/sh

set -e

celery -A restaurant_orders.celery worker --loglevel=info
