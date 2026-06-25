#!/bin/bash
# Start Celery worker in the background using the 'solo' pool to save memory
# --without-gossip --without-mingle --without-heartbeat prevents Celery from spamming Upstash Redis with ping commands
celery -A backend.celery_worker.celery_app worker --pool=solo --without-gossip --without-mingle --without-heartbeat --loglevel=info &

# Start Gunicorn in the foreground with increased threads to prevent API freezing
exec gunicorn --bind 0.0.0.0:5000 --workers 1 --worker-class gthread --threads 4 backend.app:app

# EOF