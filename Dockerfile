# Use a lightweight base image with Python
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Create the data directory and copy all files from the local data directory
RUN mkdir -p /data && chmod 777 /data
COPY data/. /data/

# Define a persistent volume for the SQLite database
VOLUME ["/data"]

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Run the script and keep the container running with sleep
CMD python3 /app/main.py && tail -f /dev/null
