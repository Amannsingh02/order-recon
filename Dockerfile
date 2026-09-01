# Production Dockerfile: multi-stage build
# Stage 1: Build Vue frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app
COPY frontend/package.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# Stage 2: Python backend with built frontend assets
FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Copy built frontend into Django static folder
RUN mkdir -p static/frontend
COPY --from=frontend-builder /app/dist/ static/frontend/

# Collect static files for WhiteNoise
RUN python manage.py collectstatic --noinput 2>/dev/null || true

EXPOSE 8000

CMD gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
