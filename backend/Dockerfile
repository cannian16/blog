FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /flask-backend

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

FROM python:3.12-slim

WORKDIR /flask-backend

COPY --from=builder /flask-backend/.venv /flask-backend/.venv
ENV PATH="/flask-backend/.venv/bin:$PATH"

COPY . .
RUN mkdir -p /flask-backend/instance

EXPOSE 5000

CMD ["uvicorn", "--app-dir", "/flask-backend/src", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]
