---
title: websocket
published: 2025-04-09
description: ''
image: ''
tags: [nginx,network,socket]
category: '系统架构'
draft: false
lang: ''
---
有时候我们需要前后端建立起持久的连接，一般的http的只能做到请求响应，他是建立了一个时间很短的socket，一来一回socket马上就断了。一般来说应用层，你要走tcp，一般就是两个比较轮椅的就是：http和websocket。udp就走QUIC。
# 传输层
## TCP
有几种比较轮椅的协议
- http：最基本的web协议，短链接，与后端服务器建立连接之后一问一答，马上关闭
- websocket：握手的时候用的http，之后变成长连接
- SSH/FTP
## UDP
- DNS
- QUIC
- Wireguard：如果使用TCP，比需要握手，就相当于明牌这个端口上有服务了
- WebRTC

这些所有的应用层协议全部都可以套一层tls或ssh。
tsl通信加密，保证隐私，通信内容可信，主要对外服务，用户无需事先交换密钥对。
ssh保证访问控制，身份安全，主要对内服务，可以事先交换密钥对。
但是这两个协议都是跑在应用层的，传输层的端口，网络层的ip，数据链路层的mac地址，对于互联网里的节点路由器来说都是完全透明的。想要完全的隐私和安全可能只能直接拉光纤了。

# websocket
要使用这个协议默认的http库一般都没有
[nodejs](https://github.com/websockets/ws) | [flask](https://flask-socketio.readthedocs.io/en/latest/)

我们一般用的http协议，一般是只有一应一答，tcp握手之后把请求给后端，后端马上响应回去，之后这个socket就断掉了，你不问服务器没法给你直接传。
但是你可使用websocket协议，他会先发一个标准的http请求，但是请求头里一般会带着一个upgrade字段。http握手后，发现请求头里有个upgrade字段，这下你就知道他不是个普通的http请求，然后就被升级成持久的socket了。
最好不要手搓socket，用websocket+http几乎已经涵盖了所有的tcp的地方了，nginx之类的代理的支持还特别好。如果你有自己的TCP协议，你还可以拿过来封装到websocket里，这样能很方便的蹭到HTTP的TLS和域名分流。
## 标准的“握手协议”
WebSocket 的 [RFC 6455 规范](https://datatracker.ietf.org/doc/html/rfc6455) 明确规定，一个合法的握手请求**必须**同时包含这两个头：
* `Upgrade: websocket`
* `Connection: Upgrade`

# nginx

```conf
# 这个map块只需要写一次就行了，因为在server块外面，作用域是整个http块。
# 是http_upgrade就是请求发过来的http头部里的upgrade字段里的值，他在这里对这个字段里的值判断，如果有值那么就把connection_upgrade这个变量赋值成upgrade。如果没有upgrade字段那么就把connection_upgrade字段设成close。
map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}

server {
    listen 80;
    server_name xxx;

    location / {
        proxy_pass http://xxx:xxx; 
        
        proxy_http_version 1.1;
        # Upgrade，Connection这种nginx默认不会传递的，你需要传给后端告诉他这个是websocket
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```