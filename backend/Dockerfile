FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.13.7 /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# 先只安装第三方依赖，uv.lock / pyproject.toml 不变时复用该层
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# 再安装项目本身；构建 wheel 需要 pyproject 中声明的 README.md
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# 迁移作为独立部署步骤执行，需要 alembic.ini 与 migrations
COPY alembic.ini ./
COPY migrations ./migrations

EXPOSE 5000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]
