# Blog

博客站点、管理后台、API 和文章内容位于同一个仓库。

## 目录

- `site/`: Astro 博客站点；文章位于 `site/src/content/posts/`
- `admin/`: SvelteKit 管理后台
- `backend/`: FastAPI API，生产数据库使用 PostgreSQL

## 本地开发

后端先复制 `backend/.env.example` 为 `backend/.env`，配置必需的 PostgreSQL `DATABASE_URL` 和其他环境变量，并执行 Alembic 迁移。然后在不同终端启动各应用：

```sh
cd backend && uv sync --frozen && uv run alembic upgrade head && uv run main.py
cd site && pnpm install && pnpm dev
cd admin && pnpm install && pnpm dev
```

`admin` 需要设置 `PUBLIC_API_BASE_URL`。`site` 的浏览器请求固定使用同源 `/api/`；本地开发前将 `site/.env.example` 复制为 `site/.env`，设置 `DEV_API_TARGET`，部署入口也需要将该路径代理到 FastAPI API。后端不再提供默认 SQLite 数据库，详细 PostgreSQL 和迁移配置见 `backend/README.md`。文章直接在 `site/src/content/posts/` 编辑，站点构建会自动读取，不再需要从独立仓库同步。

## 容器构建

各应用使用自己的目录作为 Docker build context：

```sh
docker build -t blog-backend ./backend
docker build -t blog-site ./site
docker build --build-arg PUBLIC_API_BASE_URL=https://blog.cannian.space/api -t blog-admin ./admin
docker run --rm -p 8080:80 blog-site
docker run --rm -p 3000:3000 blog-admin
```

`site` 生成静态文件，由 nginx 提供服务；音乐、友链和关于页数据由浏览器请求 `/api/` 获取，构建时无需连接后端。`admin` 使用 SvelteKit 的 Node adapter，API 地址仍由 `PUBLIC_API_BASE_URL` 构建参数指定。后端镜像需要在运行时配置 `DATABASE_URL`（PostgreSQL）、`SECRET_KEY` 和管理员凭据；镜像不会自动执行 Alembic 迁移。

## CI

`.github/workflows/` 分别检查 `site/`、`admin/` 和 `backend/`。后端 CI 使用临时 SQLite 验证 Alembic 和接口，不连接生产 PostgreSQL。相关目录变更时，PR 会运行检查并验证 Docker 构建；推送到 `main` 时，检查通过后还会发布以下镜像到 GHCR，标签为提交 SHA 的前 7 位：

- `ghcr.io/<owner>/blog-site:<sha>`
- `ghcr.io/<owner>/blog-admin:<sha>`
- `ghcr.io/<owner>/blog-backend:<sha>`

CI 不部署服务器。管理后台首页的手动部署按钮仍依赖原先的 GitHub `repository_dispatch` 流程，新的仓库配置部署流程前不能使用。
