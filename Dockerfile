# syntax=docker/dockerfile:1

FROM python:3.13-slim AS base

ENV POETRY_VERSION=2.2.0 \
    POETRY_CACHE_DIR=/root/.cache/pypoetry \
    PIP_CACHE_DIR=/root/.cache/pip

WORKDIR /app

# --- Builder stage ---
FROM base AS builder

# Install Poetry
RUN --mount=type=cache,target=$PIP_CACHE_DIR \
    pip install "poetry==${POETRY_VERSION}"

# Copy only dependency files first for better cache usage
COPY --link pyproject.toml poetry.lock ./

# Install dependencies (only main, no dev)
RUN --mount=type=cache,target=$PIP_CACHE_DIR \
    --mount=type=cache,target=$POETRY_CACHE_DIR \
    poetry config virtualenvs.in-project true && \
    poetry install --no-root --only main

# Copy the rest of the application code
COPY --link . .

# --- Final stage ---
FROM base AS final

# Create non-root user
RUN groupadd --system appuser && useradd --system --create-home --gid appuser appuser

WORKDIR /app

# Copy virtualenv and app code from builder
COPY --link --from=builder /app /app

# Ensure writable directories for logs and static files
RUN mkdir -p logs staticfiles && chown -R appuser:appuser logs staticfiles

USER appuser

ENV PATH="/app/.venv/bin:$PATH"

ENV DJANGO_SETTINGS_MODULE=config.settings

# Set placeholder secret key to avoid error loading settings.py
ENV SECRET_KEY="dummy"

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]

