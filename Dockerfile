# --- 第一阶段：构建环境 ---
FROM python:3.12-slim AS builder

# 安装 uv (直接从官方二进制安装，速度极快)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 设置工作目录
WORKDIR /flask-backend

# 只要 uv.lock 或 pyproject.toml 没变，这一层就会被缓存
# 注意：不需要手动生成 requirements.txt
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# --- 第二阶段：运行环境 ---
FROM python:3.12-slim

WORKDIR /flask-backend

# 从构建阶段拷贝已经安装好的虚拟环境
# uv 默认会创建 .venv 目录
COPY --from=builder /flask-backend/.venv /flask-backend/.venv

# 将虚拟环境的 bin 目录加入 PATH，这样直接运行 python 或 gunicorn 就会用虚拟环境里的
ENV PATH="/flask-backend/.venv/bin:$PATH"

# 复制项目代码
COPY . .

# 暴露端口
EXPOSE 5000

# 启动命令 (此时不需要再写全路径，直接调 gunicorn)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app()"]