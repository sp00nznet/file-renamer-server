FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies (curl and jq for the original script)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY run.py .
COPY file_renamer.sh .
COPY rename.sh .

# Make scripts executable
RUN chmod +x file_renamer.sh rename.sh

# Create media directory
RUN mkdir -p /media

# Expose port
EXPOSE 5000

# Set default environment variables
ENV MEDIA_DIR=/media
ENV TMDB_API_KEY=""
ENV SECRET_KEY="change-me-in-production"

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "run:app"]
