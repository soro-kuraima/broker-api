# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy over the requirements file (assume you generated it from your environment.yml)
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the application code
COPY . /app

# Create a secure directory for the database and CSV, set strict permissions
RUN mkdir -p /data && chmod 700 /data

# Set environment variables to override default paths if needed
ENV CSV_FILE_PATH=/data/backend_table.csv
ENV DATABASE_URL=sqlite:////data/app.db
ENV BACKUP_DIR=/data/broker-api-backup

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
