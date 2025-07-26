FROM python:3.11-slim

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    PIPENV_HIDE_EMOJIS=true \
    PIPENV_COLORBLIND=true \
    PIPENV_NOSPIN=true \
    PIPENV_DOTENV_LOCATION=.env

# Install required system packages including cron
RUN apt-get update && apt-get install -y \
    curl \
    python3-dev \
    build-essential \
    cron \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /code/data /code/logs

# Set up cron job for enrollment updates
RUN echo "0 * * * * cd /code && python3 enrollment_fetcher.py >> /code/logs/cron.log 2>&1" | crontab -

# Create a startup script that starts both cron and the web server
RUN echo '#!/bin/bash\n\
# Start cron service\n\
service cron start\n\
\n\
# Run initial enrollment fetch\n\
echo "Running initial enrollment fetch..."\n\
python3 enrollment_fetcher.py || echo "Initial fetch failed, will retry on next cron run"\n\
\n\
# Start the web server\n\
exec uvicorn main:app --host 0.0.0.0 --port 5000 --root-path "/smartTimetable"' > /code/start.sh

RUN chmod +x /code/start.sh

# Expose the port
EXPOSE 5000

# Use the startup script as the entry point
CMD ["/code/start.sh"]
