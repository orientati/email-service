# ---- MJML Build Stage ----
FROM node:20-alpine AS mjml_builder
WORKDIR /build
COPY package.json package-lock.json ./
RUN npm ci
COPY mjml_src ./mjml_src
# Create output directory for templates
RUN mkdir -p app/templates
RUN npm run build:emails

# ---- Python Build Stage ----
FROM python:3.13-slim AS builder
WORKDIR /app
ENV POETRY_VERSION=2.1.4
RUN pip install --no-cache-dir poetry==$POETRY_VERSION
COPY pyproject.toml poetry.lock* /app/
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi

# ---- Runtime Stage ----
FROM python:3.13-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1

# Copy installed python dependencies
COPY --from=builder /usr/local /usr/local

# Copy application code
COPY app /app/app

# Copy compiled templates from MJML stage (overwriting any local ones)
COPY --from=mjml_builder /build/app/templates /app/app/templates

# Default command: run api
CMD uvicorn app.main:app --host 0.0.0.0 --port ${SERVICE_PORT:-8000}