# Use a lightweight base image with Python
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install cron and Python dependencies
RUN apt-get update && \
    apt-get install -y cron && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create a cron job file
RUN echo "*/5 * * * * python /app/main.py >> /var/log/cron.log 2>&1" > /etc/cron.d/my-cron-job && \
    chmod 0644 /etc/cron.d/my-cron-job && \
    crontab /etc/cron.d/my-cron-job

# Ensure cron is started in the foreground with the Python script
CMD service cron start && tail -f /var/log/cron.log
