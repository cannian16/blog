# Blog

博客站点、管理后台、API 和文章内容位于同一个仓库。

## 目录

- `site/`: Astro 博客站点；文章位于 `site/src/content/posts/`
- `admin/`: SvelteKit 管理后台
- `backend/`: FastAPI API，生产数据库使用 PostgreSQL
- `bruno/`: Bruno API collection（OpenCollection YAML）

## 本地开发

后端先复制 `backend/.env.example` 为 `backend/.env`，配置必需的 PostgreSQL `DATABASE_URL` 和其他环境变量，并执行 Alembic 迁移。然后在不同终端启动各应用：

```sh
cd backend && uv sync --frozen && uv run alembic upgrade head && uv run main.py
cd site && pnpm install && pnpm dev
cd admin && pnpm install && pnpm dev
```

`admin` 和 `site` 的浏览器请求都固定使用同源 `/api/`。本地开发前分别将 `admin/.env.example`、`site/.env.example` 复制为对应的 `.env`，设置 `API_PROXY_TARGET`、`DEV_API_TARGET` 指向后端地址，Vite 会把 `/api` 代理到该地址并去掉前缀；部署入口也需要将该路径代理到 FastAPI API。后端不再提供默认 SQLite 数据库，详细 PostgreSQL 和迁移配置见 `backend/README.md`。文章直接在 `site/src/content/posts/` 编辑，站点构建会自动读取，不再需要从独立仓库同步。

## 容器构建

各应用使用自己的目录作为 Docker build context：

```sh
docker build -t blog-backend ./backend
docker build -t blog-site ./site
docker build -t blog-admin ./admin
docker run --rm -p 8080:80 blog-site
docker run --rm -p 3000:3000 blog-admin
```

`site` 生成静态文件，由 nginx 提供服务；音乐、友链和关于页数据由浏览器请求 `/api/` 获取，构建时无需连接后端。`admin` 使用 SvelteKit 的 Node adapter，浏览器同样请求同源 `/api/`，构建时不需要配置 API 地址。后端镜像需要在运行时配置 `DATABASE_URL`（PostgreSQL）、`SECRET_KEY` 和管理员凭据；镜像不会自动执行 Alembic 迁移。

## CI

`.github/workflows/` 分别检查 `site/`、`admin/` 和 `backend/`。后端 CI 使用 PostgreSQL service 验证 Alembic 和接口。相关目录变更时，PR 会运行检查、构建 Docker 镜像、执行迁移并启动容器验证 `/healthz`；推送到 `main` 时，检查通过后还会发布以下镜像到 GHCR，标签为提交 SHA 的前 7 位：

- `ghcr.io/<owner>/blog-site:<sha>`
- `ghcr.io/<owner>/blog-admin:<sha>`
- `ghcr.io/<owner>/blog-backend:<sha>`

CI 不部署服务器。管理后台的 GitHub `repository_dispatch` 部署按钮已移除，部署流程由仓库外部的 CI/CD 负责。
