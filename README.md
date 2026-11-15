# Blog

博客站点、管理后台、API 和文章内容位于同一个仓库。

## 目录

- `site/`: Astro 博客站点；文章位于 `site/src/content/posts/`
- `admin/`: SvelteKit 管理后台
- `backend/`: Flask API

## 本地开发

在对应子目录分别安装依赖并启动：

```sh
cd backend && uv sync && uv run main.py
cd site && pnpm install && pnpm dev
cd admin && pnpm install && pnpm dev
```

`admin` 需要设置 `PUBLIC_API_BASE_URL`；`site` 可通过 `PUBLIC_API_BASE` 设置 API 地址。后端需要按 `backend/README.md` 配置环境变量。

## 容器构建

各应用使用自己的目录作为 Docker build context：

```sh
docker build -t blog-backend ./backend
docker build -t blog-site ./site
docker build --build-arg PUBLIC_API_BASE_URL=https://blog.cannian.space/api -t blog-admin ./admin
```

`site` 和 `admin` 的 API 地址在构建时写入产物。部署前按目标环境设置对应 build arg；`site` 生成静态文件，由 nginx 提供服务，`admin` 使用 SvelteKit 的 Node adapter。
