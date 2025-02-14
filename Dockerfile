# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the application code, including the initial_data folder
COPY . /app

# Prepopulate /data with the initial CSV file.
# We copy the file into /data before declaring it as a volume.
RUN mkdir -p /data && \
    cp data/csv/backend_table.csv /data/backend_table.csv && \
    chmod 700 /data/backend_table.csv

# Declare /data as a Docker-managed volume.
# When the container starts with a new volume, Docker will copy the content
# from the image’s /data directory into the volume.
VOLUME ["/data"]

# Set environment variables for your application to use the secure /data location.
ENV CSV_FILE_PATH=/data/backend_table.csv
ENV DATABASE_URL=sqlite:////data/app.db
ENV BACKUP_DIR=/data/broker-api-backup

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
