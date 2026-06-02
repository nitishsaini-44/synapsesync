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
COPY . .

# Environment variables
ENV FLASK_ENV=production
ENV FLASK_PORT=5000
ENV PYTHONPATH=/app/..

EXPOSE 5000

# Run gunicorn
# Notice: since we copy backend/ into /app, app.py is at /app/app.py
# If pythonpath is needed, we should run gunicorn with the correct module path
# If we set workdir to /app and run gunicorn app:app, it works if app.py is in /app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
