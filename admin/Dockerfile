# --- 第一阶段：构建 SSR 产物 ---
FROM node:22-alpine AS builder
RUN corepack enable
WORKDIR /app

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .
RUN pnpm build

# --- 第二阶段：运行 ---
# adapter-node 的产物是自包含的，运行镜像不需要再安装依赖
FROM node:22-alpine AS runner
WORKDIR /app

COPY --from=builder /app/build ./build
# 保留 "type": "module"，让 Node 明确按 ESM 加载 build/index.js
COPY --from=builder /app/package.json ./

# adapter-node 默认监听 0.0.0.0:3000，可用 PORT / HOST 环境变量覆盖
EXPOSE 3000

CMD ["node", "build"]
