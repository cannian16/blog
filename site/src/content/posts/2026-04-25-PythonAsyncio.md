---
title: python异步
published: 2026-04-25
description: '用了这么久的python，js的异步，但是里面一直没有细究'
image: ''
tags: ['asyncio','python']
category: '语言和框架'
draft: false
lang: ''
---
一直以来，对异步的理解都停留在可用的地步，比如async是承诺我这个函数将来会返回值，await就是遇到这种async的函数，我就在这中断，等这个async返回，我先去做别的协程的任务，但真实的异步远不止于此。

如果不熟悉异步的话建议先看一下asyncio的[文档](https://docs.python.org/zh-cn/3.14/library/asyncio.html)，python的异步和js还是不太一样的。
# 异步
异步的本质只有一件事：利用在进行io读写的 CPU 闲置时间去处理其他任务。
这个是最基本的异步函数，其实在async函数内部是完全线性的，但是有await的存在，提供了一个断点让他在io中断的时候，别的协程可以在这里插入进去，去执行他们的任务。
```python
import asyncio
import time
async def async_task():#这就是定义一个协程(coroutine)
    a = 1#阻塞
    print("abc")#阻塞
    time.sleep(3)#这里是完全塞的3秒，期间线程不会有任何并发
    await other_async_task()#这个里面其实里面可能嵌套了很深的async函数，每一层都和async函数一样。
```
但是实际上这个异步函数真正能起作用压根不在await上，如果你要能被中断变成真正的异步async_task函数里一定会有以下几种系统调用发生
- 网络通信：epoll_ctl / epoll_wait
- 文件操作：read / write
- 线程休眠：内核Timer
只有很少的几种能实现真正的异步，而我们真正用到异步的其实也只有网络的socket io了，如果这个异步函数里没有任何一个是系统注册的可中断的，就算有多少await也是白费的，根本没地方让别的协程插进去。所以异步对供应链的要求非常高，如果某个库看起来定义了async函数，你也能用await调用，如果底层没用之前提到的这几个，那多半还是同步阻塞的。比如：
```python
In [4]: async def async_task():
   ...:     time.sleep(3)
#中间等的3秒期间这个线程是被完全阻塞的，其他协程完全没办法插入
In [5]: await async_task()
```
但是如果你还是想要异步，比如你的web后端接收请求的进程不想被同步阻塞，可能需要可能需要更高层次的异步了
## 线程池
比如你有类似于time.sleep这种的阻塞业务，你就可以像java一样多开线程池，线程越多越吃内存和cpu切换，这样主线程就不会被阻塞了。对于超高并发和重量级的阻塞，这种因为会有大量的cpu切换的时间，反而会让主进程响应时间边长
## 分布式
比如一个比较经典的技术栈：fastapi+redis+taskiq，fastapi前台负责异步大批量的接收请求，然后把需要阻塞的任务需求扔到redis里，然后taskiq后端一个个慢慢的处理任务。这种是跨进程，甚至可以跨服务器的分布式架构，通过socket进行通信。这种异步分布式架构几乎是大型项目的必选项。
## 编排
异步实际上我们有时候，不希望一堆协程一起下载，下载完了一起处理，可能这种异步架构反而会拖慢qps，我们可以控制并发流，比如同时可以有10个并发下载，5个并发处理，前面一批在处理，刚好后面一批在下载，io和cpu处理刚好错峰。
# 实践
官方文档里有个这样的[示例代码](https://docs.python.org/zh-cn/3.14/library/asyncio-task.html#running-tasks-concurrently)：
```python
import asyncio

async def factorial(name, number):
    f = 1
    for i in range(2, number + 1):
        print(f"Task {name}: Compute factorial({number}), currently i={i}...")
        await asyncio.sleep(1)
        f *= i
    print(f"Task {name}: factorial({number}) = {f}")
    return f

async def main():
    # *并发地* 调度这三次调用：
    L = await asyncio.gather(
        factorial("A", 2),
        factorial("B", 3),
        factorial("C", 4),
    )
    print(L)

asyncio.run(main())

# 预期的输出：
#
#     Task A: Compute factorial(2), currently i=2...
#     Task B: Compute factorial(3), currently i=2...
#     Task C: Compute factorial(4), currently i=2...
#     Task A: factorial(2) = 2
#     Task B: Compute factorial(3), currently i=3...
#     Task C: Compute factorial(4), currently i=3...
#     Task B: factorial(3) = 6
#     Task C: Compute factorial(4), currently i=4...
#     Task C: factorial(4) = 24
#     [2, 6, 24]

#如果你使用这种方法来写异步函数，其实是假的异步因为一个协程之内是完全线性的，可以说await和async完全不重要，重要的是gather，是他把一大堆协程放到了池子里一起跑，见缝插针的把await出来的空隙填满的
async def fake_async():
    await factorial("A", 2)
    await factorial("B", 3)
    await factorial("C", 4)
asyncio.run(fake_async())
#我自己跑了一遍，很显然不是并发的
In [9]: asyncio.run(fake_async())
Task A: Compute factorial(2), currently i=2...
Task A: factorial(2) = 2
Task B: Compute factorial(3), currently i=2...
Task B: Compute factorial(3), currently i=3...
Task B: factorial(3) = 6
Task C: Compute factorial(4), currently i=2...
Task C: Compute factorial(4), currently i=3...
Task C: Compute factorial(4), currently i=4...
Task C: factorial(4) = 24
```