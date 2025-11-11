# Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (optional but useful for SSL/certs and timezone)
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates tzdata && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt ./
RUN pip install --upgrade --no-cache-dir pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Expose the port your app will listen on inside the container
EXPOSE 8000

# Provide sensible defaults that still honour runtime configuration
ENV PORT=8000 \
    WEB_CONCURRENCY=2

# Start Gunicorn, binding to the Fly-provided PORT if present
CMD ["sh", "-c", "gunicorn -w ${WEB_CONCURRENCY:-2} -b 0.0.0.0:${PORT:-8000} app:application"]
