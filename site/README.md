# 简介
从[saicaca/fuwari](https://github.com/saicaca/fuwari/tree/main)fork来的，添加了东西，但并未使用i18n的开发规范。
添加了友链，留言板，音乐还有一些小组件。目前正在把这个项目从静态页面往前后端分离的架构转移，想看完整的部署教程请移步fuwari的主分支。

站点请求同源 `/api/`。本地开发由 Astro 将其代理到 `127.0.0.1:5000`；容器部署时需要在入口反向代理中将 `/api/` 转发到 Flask，并去掉 `/api` 前缀。
