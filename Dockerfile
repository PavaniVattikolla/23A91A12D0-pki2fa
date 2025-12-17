# Multi-stage build for PKI 2FA Microservice
FROM python:3.11-slim as builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

# Set timezone to UTC (CRITICAL!)
ENV TZ=UTC
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends cron tzdata && \
    ln -snf /usr/share/zoneinfo/UTC /etc/localtime && \
    echo "UTC" > /etc/timezone && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY app.py .
COPY student_private.pem .
COPY student_public.pem .
COPY instructor_public.pem .
COPY scripts/ ./scripts/

# Setup cron job
COPY cron/2fa-cron /etc/cron.d/pki2fa-cron
RUN chmod 0644 /etc/cron.d/pki2fa-cron && \
    crontab /etc/cron.d/pki2fa-cron && \
    touch /var/log/cron.log

# Create volume mount points
RUN mkdir -p /data /cron && chmod 755 /data /cron

# Expose port
EXPOSE 8080

# Start cron and application
CMD cron && uvicorn app:app --host 0.0.0.0 --port 8080
