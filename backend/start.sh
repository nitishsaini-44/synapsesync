#!/bin/bash
# Start Celery worker in the background using the 'solo' pool to save memory
# --without-gossip --without-mingle --without-heartbeat prevents Celery from spamming Upstash Redis with ping commands
celery -A backend.celery_worker.celery_app worker --pool=solo --loglevel=info &

# Start Gunicorn in the foreground with reduced threads to stay under 512MB RAM
exec gunicorn --bind 0.0.0.0:5000 --workers 1 --worker-class gthread --threads 2 backend.app:app
