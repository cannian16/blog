# 应用的CLI命令
下面所有的命令的工作路径都在项目的根目录

## 初始化数据库
在utils/commands.py里注册的命令
```bash
#flask自动发现应用工厂的方式创建数据库
uv run flask init-db
#显式指定应用工厂入口--app <包名>:<函数名>
uv run flask --app app:create_app init-db
```

## 启动开发服务器
```bash
# 传统方式,把app包导出来执行工厂函数赋给实例，执行run方法
uv run main.py
# 显式指定包和creat_app函数
flask --app app:create_app run --debug
# 自动识别create_app函数，并运行实例
uv run flask run
```

## 启动生产服务器(-w 参数调整进程(work)数)
 uv run gunicorn -w 4 -b 127.0.0.1:5000 "app:create_app()"

# 项目结构
项目结构典的不能再典了，不用说了就，很简单的项目。

# 注意事项
## 环境变量
```text
SECRET_KEY=:"dev"
ALLOWED_ORIGINS="http://localhost:4321"
GITHUB_REPO="xxxx/xxxx"
ADMIN_USERNAME="cannian"
ADMIN_PASSWORD="20050113Xhz."
GITHUB_TOKEN=""
```
```docker-compose.yml
services:
  flask_backend:
    imsage: flask_backend:latest
    container_name: flask_backend
    environment:
      TZ: "Asia/Shanghai"
    volumes:
      - ./instance:/flask_backend/instance
    ports:
      - "5000:5000"
```