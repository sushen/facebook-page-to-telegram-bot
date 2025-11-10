# Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (optional but useful for SSL/certs and timezone)
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates tzdata && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Expose the port your app will listen on inside the container
EXPOSE 8080

# Start with gunicorn, pointing at the WSGI app object "application" in app.py
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8080", "app:application"]
