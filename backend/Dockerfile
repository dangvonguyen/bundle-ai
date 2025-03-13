FROM python:3.12-slim AS base

WORKDIR /app

RUN groupadd -r app && useradd -r -g app app

FROM base AS builder

COPY --from=ghcr.io/astral-sh/uv:0.6.1 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev --no-editable

COPY . .

FROM base AS runtime

COPY --from=builder --chown=app:app /app /app

USER app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]