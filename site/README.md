# 简介
从[saicaca/fuwari](https://github.com/saicaca/fuwari/tree/main)fork来的，添加了东西，但并未使用i18n的开发规范。
添加了友链，留言板，音乐还有一些小组件。目前正在把这个项目从静态页面往前后端分离的架构转移，想看完整的部署教程请移步fuwari的主分支。

站点请求同源 `/api/`。本地开发前复制 `.env.example` 为 `.env`，设置 `DEV_API_TARGET` 为 FastAPI 服务地址。Astro 开发服务器会将 `/api/` 代理到该地址并去掉 `/api` 前缀；未设置该变量时不启用开发代理。容器部署时需要在入口反向代理中做同样的路径转发。
