---
title: Linux底层
published: 2025-04-01
description: 'linux'
image: ''
tags: [linux,文件系统]
category: '系统架构'
draft: false
lang: ''
---
# 指令流
## 系统指令（用户态）
可以通过which <某个指令>，来查看这个指令的位置在哪。
### Shell Built-in（内建指令）
如 `cd`、`alias`、`export`。
    * 这种指令是有关shell的进程状态的，需要改变shell的工作路径，所以无法通过普通的命令来实现
### External Binaries（外部二进制文件）
如 `ls`、`python3`、`sqlite3`。
这种就是最普通的二进制文件了，正常需要指定完全的路径的，可以通过环境变量来让他在任意目录直接运行，变成进程。
但不是所有的文件或者二进制文件可以被执行，主要是内核看他的前4个字节`0x7f 'E' 'L' 'F'`

## glibc（用户态）
ldd可以指明这个二进制文件调用了哪些库。比如：`ldd $(which python3)`
标准库，把二进制文件里调用<stdio.h>的里的printf，malloc之类的函数，翻译成汇编指令，把参数变成放到寄存器里，然后系统调用等内核来操作硬件
<stdio.h>这种头文件是C语言的标准组织制定的标准，但是具体落实到各个系统上需要GNU，微软，把函数和系统调用对起来。
有些文件比如go编译出来的二进制文件是自带了需要调用的那些库的，所以ldd就查不出他的依赖。

## 系统调用（用户态->内核态）
会进行执行那些需要对硬件进行交互的指令，你要先把需要打印到屏幕或者是保存到硬盘的值先准备好，然后使用systemcall(RAX),RAX是告诉内核你想要调用什么，然后内核代替你用内核态把你准备好的东西按照你的调用来操作硬件。

比如说你执行了一个
```python
print("hello")
python解释器把他变成下面
printf("hello\n")
glibc把c变成汇编对寄存器赋值，然后systemcall等内核来操作硬件
然后内核进行最终的指令来控制屏幕。
```
# 文件系统
这些输出的本质上就是inode上的元数据。
## 软链接
lrwxrwxrwx 1 cannian Users   17 Jan 16 20:00 file -> /realpath
## 目录
drwxr-xr-x 2 cannian Users 4.0K Apr  1 01:11 xxxx
## socket套接字
srwxr-xr-x 1 cannian Users    0 Apr  1 01:01 xxx.sock
## 字符流设备
流式的，不能随机读这个设备，只能像水管一样流一点读一点。
### 终端
crw--w---- 1 cannian pts  136, 0 Apr  1 22:33 0
是一个双向的可读可写，既可以当标准输出也能是标准输入。
是你连接终端用键盘把字母打进去存的一个缓冲区，就和输入框一样，你按一个回车就把这个输入框的所有的东西全部交给了zsh，bash这种shell，比如输入的是`python hello.py`,
经过解析，去找对应的指令，他会把python输出的`hello world`这个标准输出写回到pts里，就显示结果到你的终端里了。他只负责输入输出。你的终端里的上面的历史记录是由宿主机的`powershell、xshell`这种管理的，
指令历史记录是由服务器的zsh，bash管理的
### 摄像头
crw--w---- 1 cannian vedio0  136, 0 Apr  1 22:33 0
当你open这个文件的时候就代表你要使用摄像头了，会申请几个buffer缓存在内存里
| 内存位置 | 状态 | 内容 |
| :--- | :--- | :--- |
| **Buffer 0** | 正在写入 | [ 0xFF 0xD8 ... 写入中 ] |
| **Buffer 1** | 已满 | [ 上一帧完整的图片数据 ] |
| **Buffer 2** | 待读取 | [ OpenCV 正在解析这一帧 ] |
| **Buffer 3** | 空闲 | [ 等待下一轮循环 ] |
然后你就轮流一块一块轮流读，摄像头通过dma直接往需要写入的已经被读完的内存块里写。
## 块设备
能够随机读写某个块想读什么就读什么，直接读写硬盘的扇区，读出的是16进制数据，因为没有文件系统所以没有意义
brw-rw----  1 root disk    259,    0 Mar 30 16:32 nvme0n1
## 文件或硬链接
-rw-rw----+ 1 cannian Users 107 Mar 31 18:22 makefile
## iSCSI和reclone
iSCSI是从物理硬盘入手，直接模拟成在/dev里的物理网卡，需要进行分区、文件系统和挂载，reclone是直接在文件系统模拟成具体文件的