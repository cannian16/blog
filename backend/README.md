# Blog FastAPI Backend

以下命令均在 `backend/` 目录执行。

## 安装依赖

```sh
uv sync --frozen
```

## 环境变量

复制并按部署环境配置 `.env`：

```text
SECRET_KEY="replace-with-a-strong-secret"
ALLOWED_ORIGINS="http://localhost:4321"
GITHUB_REPO="owner/repository"
ADMIN_USERNAME="admin"
ADMIN_PASSWORD="replace-me"
GITHUB_TOKEN=""
```

默认数据库仍为 `instance/app.db`，可通过 `DATABASE_URL` 覆盖。

## 初始化数据库

```sh
uv run main.py init-db
```

该命令会自动创建 `instance/` 目录，并仅调用 SQLAlchemy `create_all` 创建缺失表；不会删除表、迁移或覆盖已有 `app.db`。

## 启动服务

开发环境：

```sh
uv run main.py
```

直接使用 Uvicorn：

```sh
uv run uvicorn --app-dir src app.main:app --host 0.0.0.0 --port 5000
```

## 测试

```sh
uv run pytest
```

测试使用 pytest 提供的临时 SQLite 数据库，不读写 `instance/app.db`。

## Docker

```sh
docker build -t blog-backend .
docker run --rm \
  -p 5000:5000 \
  -v "$(pwd)/instance:/flask-backend/instance" \
  --env-file .env \
  blog-backend
```

容器继续使用 `/flask-backend` 和 `/flask-backend/instance`，因此旧 SQLite volume 挂载路径保持兼容。镜像启动不会自动初始化、迁移或覆盖数据库。
