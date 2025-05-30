# Stage 1: Builder
FROM python:3.10-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Stage 2: Final
FROM python:3.10-slim

WORKDIR /app

COPY --from=builder /usr/local /usr/local

COPY . .

RUN mkdir -p /app/images && chmod -R 755 /app/images

EXPOSE 8081

CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:8081", "--log-level", "info"]