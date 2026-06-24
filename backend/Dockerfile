FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
# We expect the context to be the project root, so we copy the backend folder
# Actually, the docker-compose specifies `build: ./backend`, so context is `backend/`
COPY . /app/backend/

# Environment variables
ENV FLASK_ENV=production
ENV FLASK_PORT=5000
ENV PYTHONPATH=/app

EXPOSE 5000

# Make start.sh executable
RUN chmod +x /app/backend/start.sh

# Run the start script which boots both Celery and Gunicorn
CMD ["/app/backend/start.sh"]
