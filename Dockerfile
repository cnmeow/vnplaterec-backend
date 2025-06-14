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

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
  && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local /usr/local

COPY . .

RUN mkdir -p /app/images && chmod -R 755 /app/images

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
