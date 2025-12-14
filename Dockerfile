FROM python:3.11-slim

# Install cron
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Setup cron job if cron file exists
RUN if [ -f cron/2fa-cron ]; then \
    cp cron/2fa-cron /etc/cron.d/pki2fa-cron && \
    chmod 0644 /etc/cron.d/pki2fa-cron && \
    crontab /etc/cron.d/pki2fa-cron && \
    touch /var/log/cron.log; \
    fi

# Create start script
RUN echo '#!/bin/bash\ncron\nuvicorn app:app --host 0.0.0.0 --port 8000' > /start.sh && \
    chmod +x /start.sh

EXPOSE 8000

CMD ["/start.sh"]
