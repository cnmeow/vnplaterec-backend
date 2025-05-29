# Use official Python image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
RUN mkdir -p /app/images && chmod -R 777 /app/images
COPY . .

# Expose port
EXPOSE 8081

# Run the app
CMD ["python", "app.py"]
