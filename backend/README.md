# Blog FastAPI Backend

以下命令均在 `backend/` 目录执行。

## 安装依赖

```sh
uv sync --frozen
```

## PostgreSQL 与环境变量

生产和本地运行均必须提供 `DATABASE_URL`，不再回退到 SQLite。复制示例并填写 PostgreSQL 连接信息：

```sh
cp .env.example .env
```

```text
DATABASE_URL="postgresql://blog_user:password@localhost:5432/blog"
SECRET_KEY="replace-with-a-strong-secret"
DEBUG="false"
ADMIN_USERNAME="admin"
ADMIN_PASSWORD="replace-me"
GITHUB_REPO="owner/repository"
GITHUB_TOKEN=""
```

应用通过 `python-dotenv` 加载 `backend/.env`；缺少 `DATABASE_URL` 时会在启动阶段给出明确错误。SQLite 仅用于隔离测试。

## 数据库迁移

首次初始化和后续升级都使用原生 Alembic：

```sh
uv run alembic upgrade head
# 或
make migrate
```

应用和 Docker 镜像启动时不会自动迁移，也不会调用 `create_all`。部署时应在启动新版本前单独执行迁移命令。

## 启动服务

```sh
uv run main.py
# 或
make dev
```

`main.py` 使用 Uvicorn 在 `0.0.0.0:5000` 启动 FastAPI。也可以直接运行：

```sh
uv run uvicorn --app-dir src app.main:app --host 0.0.0.0 --port 5000
```

## 调试模式

将 `DEBUG` 设为 `true`（大小写不敏感，也接受 `1`、`yes`、`on`）后：

- 开启 FastAPI 自带的接口文档：`/docs`（Swagger UI）、`/redoc`、`/openapi.json`
- 日志级别切换为 `DEBUG`，包括 uvicorn 访问日志和应用日志（SQLAlchemy 的 SQL 日志也会输出）

`DEBUG` 未设置或为 `false` 时，上述三个文档路径返回 404，保持与上游 Flask 接口兼容的行为。

## 测试与检查

```sh
make test
uv run ruff check src tests main.py migrations
uv run python -m compileall -q src tests main.py migrations
```

测试在导入应用前设置临时 SQLite `DATABASE_URL`；Alembic 测试也只升级临时 SQLite 数据库，不连接 PostgreSQL。

## Docker

```sh
docker build -t blog-backend .
docker run --rm -p 5000:5000 --env-file .env blog-backend
```

容器不创建或挂载 `instance/`，也不会自动执行迁移。运行容器前需针对配置的 PostgreSQL 数据库执行 `uv run alembic upgrade head`（可作为独立部署步骤或一次性任务）。
