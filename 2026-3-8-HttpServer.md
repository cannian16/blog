---
title: web基础
published: 2026-03-08
description: 'http服务器和网关接口和web框架'
image: ''
tags: ['python']
category: '系统架构'
draft: false
lang: ''
---
# http服务器
tomcat，gunicorn，uvicorn，nginx，这些http服务器，他可以处理TCP握手、http请求的解析和转发、管理worker进程、自动重启、负载均衡之类的。然后通过协议和app业务逻辑通信，今昔那个下一步的路由判断之类的。
其实nginx也算一个http服务器，虽然大部分人可能用他进行负载均衡反向代理的，但是他能处理http连接，你甚至可以用c来用nginx直接处理业务，但是用web框架能让我们写业务写的更爽。
# Web 框架
flask，django，fastapi这些后端web框架只知道业务逻辑，但并看不懂一个普通的tcp socket。所以他们只能产生一个符合wsgi/asgi规范的web应用，然后等着被http服务器调用，然后进行后续的路由分发，业务逻辑之类的。web框架压根不懂web，他只是专门处理业务逻辑的。你甚至可以不依赖http服务器来调用web框架，你按照协议给app传参，他就给你返回response了。

# WSGI和ASGI
WSGI/ASGI是一个协议，是http服务器和web后端框架统一的通信协议，http服务器，接收socket连接，解析出了请求的数据，根据WSGI的协议去调用web框架的WSGI的app对象，
## [WSGI](https://wsgi.readthedocs.io/en/latest/)
把app给喂给他，首先他创建了一个gunicorn主进程，专门管理gunicorn的子进程，每个子进程都监听同一个端口，有一个完整的http服务器，解析http请求，并传给app对象让他响应。

下面根据WSGI协议做个最简单的web应用，代码来自https://peps.python.org/pep-3333/#the-application-framework-side。
编写最简单的wsgi应用
```python
#test.py
HELLO_WORLD = b"Hello world!\n"

def simple_app(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/plain')]
    start_response(status, headers)
    return [HELLO_WORLD]
```
启动http服务器
```bash
uv run gunicorn -w 4 -b 127.0.0.1:5000 "test:simple_app" 
```
访问5000端口，会发现HelloWorld被返回了，web框架做的实际上就和那个simple_app差不多，只不过有更系统性的路由匹配规则之类的
## [ASGI](https://asgi.readthedocs.io/en/latest/index.html)
ASGI支持异步，一般来说是单个主线程单进程，WSGI一般是阻塞的，所以我们可以设置work进程数量，来提高并发，但是gunicorn的进程管理模块实际上可以用到uvicorn上。
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

下面来试试不用uvicorn，来手动调用fastapi的app对象吧
```python
#main.py
#这个是个最简单的fastapi的app对象了，符合ASGI协议
app = FastAPI(
    docs_url="/docs" if os.getenv("DEBUG") == "True" else None
)

@app.get("/")
async def read_items():
    return {"message": "Hello World"}
```
```python title="Ipython
In [1]: from app.main import app

In [2]: import asyncio

In [3]: scope = {
   ...:     "type": "http",
   ...:     "http_version": "1.1",
   ...:     "method": "GET",
   ...:     "path": "/",
   ...:     "root_path": "",          
   ...:     "scheme": "http",         
   ...:     "query_string": b"",      
   ...:     "headers": [              
   ...:         (b"host", b"localhost"),
   ...:         (b"accept", b"*/*"),
   ...:     ],
   ...:     "client": ("127.0.0.1", 11451), 
   ...: }

In [4]: async def mock_receive():
   ...:     return {"type": "http.request", "body": b""}

In [5]: responses = []

In [6]: async def mock_send(message):
   ...:     responses.append(message)   

In [7]: async def run_manual():
   ...:     await app(scope, mock_receive, mock_send)
   ...:     # 打印结果
   ...:     print("--- 框架吐出的原始 ASGI 消息 ---")
   ...:     for msg in responses:
   ...:         print(msg)
In [8]: await run_manual()
--- 框架吐出的原始 ASGI 消息 ---
{'type': 'http.response.start', 'status': 200, 'headers': [(b'content-length', b'25'), (b'content-type', b'application/json')]}
{'type': 'http.response.body', 'body': b'{"message":"Hello World"}'}
```
 
别人的博客：[](https://samagra.me/wtf/2024/09/27/gateway-interfaces.html)