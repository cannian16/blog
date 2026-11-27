# --- 第一阶段：编译 (全量安装) ---
FROM node:22-slim AS builder
RUN corepack enable
WORKDIR /app

COPY package.json pnpm-lock.yaml ./
# 这里装了所有 devDependencies，为了能跑 pnpm build
RUN pnpm install --frozen-lockfile

COPY . .
RUN pnpm build

# --- 第二阶段：运行 (精简安装) ---
FROM node:22-slim AS runner
RUN corepack enable
WORKDIR /app

# 1. 只把构建好的成品拿过来
COPY --from=builder /app/build ./build
COPY --from=builder /app/package.json .
COPY --from=builder /app/pnpm-lock.yaml .

# 2. 【核心改动】在生产环境镜像里只安装 dependencies
# 这样像 Vite、Tailwind、TypeScript 这些几百MB的东西都不会出现在最终镜像里
RUN pnpm install --prod --frozen-lockfile

ENV NODE_ENV=production
ENV PORT=3000
EXPOSE 3000

CMD ["node", "build"]
