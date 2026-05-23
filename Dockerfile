FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

FROM python:3.13-slim AS runtime

RUN useradd --create-home --shell /bin/bash app

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app"

COPY --from=builder /app/.venv /app/.venv

COPY --chown=app:app ./src/main.py ./

USER app

EXPOSE 8082

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8082"]