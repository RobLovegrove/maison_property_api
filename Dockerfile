FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install -r requirements.txt gunicorn

# Copy application code
# Add a build argument for cache busting if needed
ARG CACHEBUST=1
COPY . .

# Set environment variables
ENV FLASK_APP=wsgi.py \
    FLASK_ENV=production \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    AZURE_STORAGE_CONNECTION_STRING=""

# Expose port
EXPOSE 8000

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run using gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "wsgi:app", "--log-level", "debug"] 