#!/bin/bash
# Start Celery worker in the background
celery -A backend.celery_worker.celery_app worker --loglevel=info &

# Start Gunicorn in the foreground
exec gunicorn --bind 0.0.0.0:5000 --workers 1 --worker-class gthread --threads 4 backend.app:app
