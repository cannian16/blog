---
title: python 上下文和生成器
published: 2026-05-05
description: '关于python的上下文和生成器'
image: ''
tags: ['python']
category: '语言和框架'
draft: false
lang: ''
---
# 生成器
我们先来试试这个片段
```python
In [1]: def my_generator():
   ...:     print("--- 准备开始往外拉 ---")
   ...:     yield "拉第一次"  # 暂停在这里，并返回
   ...: 
   ...:     print("--- 继续拉 ---")
   ...:     yield "拉第二次"  # 再次暂停，并返回
   ...: 
   ...:     print("--- 完事了 ---")
In [2]: gen = my_generator()
In [3]: next(gen)
--- 准备开始往外拉 ---
Out[3]: '拉第一次'
In [4]: next(gen)
--- 继续拉 ---
Out[4]: '拉第二次'
In [5]: next(gen)
--- 完事了 ---
---------------------------------------------------------------------------
StopIteration                             Traceback (most recent call last)
Cell In[5], line 1
----> 1 next(gen)

StopIteration: 
#没有return因为没有写yield,rasie了一个停止迭代异常
```
感受到了吗，就是一点一点生产把有的给拉出来。本质上其实就是实现了这个gen对象的__next__()方法。我们可以不用yield用元编程来手动实现一下生成器。
```python
In [5]:class MyManualGenerator:
...:       def __init__(self):
...:           self.state = 0
...:   
...:       def __iter__(self):
...:           # 迭代器协议规定：__iter__ 必须返回迭代器对象本身
...:           return self
...:   
...:       def __next__(self):
...:           if self.state == 0:
...:               print("--- 准备开始往外拉 ---")
...:               self.state = 1
...:               return "拉第一次"
...:           
...:           elif self.state == 1:
...:               print("--- 继续拉 ---")
...:               self.state = 2
...:               return "拉第二次"
...:           
...:           else:
...:               print("--- 完事了 ---")
...:               # 当没有东西可以 yield 时，必须抛出这个异常
...:               # 这样 for 循环或框架才知道“牙膏”挤完了，except捕获这个异常然后跳出迭代
...:               raise StopIteration()
```
这个玩意用next()效果和上面用yield写出来的效果一毛一样，就像之前说的鸭子类型，只要你有__next__()和state就能被next()或者for调用
```python
In [6]: gen = MyManualGenerator()
In [7]: for i in gen:
    ...:     print(i)
    ...: 
--- 准备开始往外拉 ---
拉第一次
--- 继续拉 ---
拉第二次
--- 完事了 ---
```

# 上下文
我们经常在调用某个函数之后，还想接着跑那个函数剩下的东西。比如数据库session我们肯定希望业务那边无感调用，用完了自动把session还回去，不然一堆session在那边会挤爆数据库连接池和内存。这个时候就也要用到这个yield，你看是不是和生成器一模一样。在你需要session的时候，执行一下next()把session拿到了，然后用完了再执行一次next()，把session给close了。
```python
#伪代码
def get_session():
    session = Session(engine)#这个engine是数据库配置。
    yield session
    session.close()#假设session实例有一个关闭数据库会话的函数
gen = get_session()
session = next(gen)#获取那个yield返回的session并停在那。
#---------你的业务逻辑
#session.add()
#session.commit()
#-------业务结束
next(gen)#调用session.close
```
这就是框架和orm给我们做的底层逻辑比如
- fastapi会这样注入上下文：`session: Session = Depends(get_session)`
- taskiq这样：`session: Session = TaskiqDepends(get_session)`
感受到了这些框架了吗，其实大同小异，一个模子里刻出来的。
## with
但是python有个语法糖，为了方便开发，一般我们获取session是这样的。
```python
def get_session():
    with Session(engine) as session:
        yield session
```
意思是如果代码运行出了with语句块自动进行session.close()，断开数据库会话。很明显不能白白的就自动的给你关了数据库连接，with要求Session必须有`__entry__`和`__exit__`才能用这个语法糖，从名字也能看出来，进入和退出。
这个Session类就像下面这样。
```python
class Session:
    def __init__(self, engine):
        self.engine = engine

    def __enter__(self):
        # 建立连接
        return self  # 返回给 'as session' 的那个变量

    def __exit__(self):
        # 当走出了with语句块自动执行
        self.close()
    
    def close(self):
        # 关闭逻辑
        pass
```