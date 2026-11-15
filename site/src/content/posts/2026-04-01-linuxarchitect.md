---
title: Linux内核
published: 2026-04-01
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
[别人的文章](https://dev.to/kanywst/linux-file-system-architecture-a-deep-dive-into-vfs-inodes-and-storage-1n9) | [文档](https://docs.kernel.org/filesystems/vfs.html)
## Inode
可以说inode其实就代表着一个物理文件，硬件设备本身，通过inode才能找到数据的`Block Map`。Inode就是物理数据的逻辑化身，如果没了Inode这些二进制数据全部变成散沙，迷失在硬盘里了，单纯的二进制数据没有任何意义是逻辑对他们编码赋予了意义。
`ll`和`stat <path>`可以输出Inode的内容
```bash
#inode里是不存文件名的，这个文件名是存在父路径的数据块里，有文件名与indoe号的映射
  Size: 44              Blocks: 0          IO Block: 4096   directory
Device: 0,59    Inode: 7887        Links: 1 
Access: (0771/drwxrwx--x)  Uid: ( 1000/ cannian)   Gid: ( 1001/   Users)
Access: 2026-04-09 17:26:34.689442991 +0800
Modify: 2026-04-08 14:18:32.584766593 +0800
Change: 2026-04-08 14:18:32.584766593 +0800
Birth: 2026-01-16 16:41:55.955698670 +0800
```
### 软链接
lrwxrwxrwx 1 cannian Users   17 Jan 16 20:00 file -> /realpath
### 目录
drwxr-xr-x 2 cannian Users 4.0K Apr  1 01:11 xxxx
### socket
网卡本身并不会出现在/dev里，但是每个经过系统封装的socket连接都会变成一个Inode作为一个io设备出现在文件系统
srwxr-xr-x 1 cannian Users    0 Apr  1 01:01 xxx.sock
### 字符流设备
流式的，不能随机读这个设备，只能像水管一样流一点读一点。
#### 终端
crw--w---- 1 cannian pts  136, 0 Apr  1 22:33 0
是一个双向的可读可写，既可以当标准输出也能是标准输入。
是你连接终端用键盘把字母打进去存的一个缓冲区，就和输入框一样，你按一个回车就把这个输入框的所有的东西全部交给了zsh，bash这种shell，比如输入的是`python hello.py`,
经过解析，去找对应的指令，他会把python输出的`hello world`这个标准输出写回到pts里，就显示结果到你的终端里了。他只负责输入输出。你的终端里的上面的历史记录是由宿主机的`powershell、xshell`这种管理的，
指令历史记录是由服务器的zsh，bash管理的
#### 摄像头
crw--w---- 1 cannian vedio0  136, 0 Apr  1 22:33 0
当你open这个文件的时候就代表你要使用摄像头了，会申请几个buffer缓存在内存里
| 内存位置 | 状态 | 内容 |
| :--- | :--- | :--- |
| **Buffer 0** | 正在写入 | [ 0xFF 0xD8 ... 写入中 ] |
| **Buffer 1** | 已满 | [ 上一帧完整的图片数据 ] |
| **Buffer 2** | 待读取 | [ OpenCV 正在解析这一帧 ] |
| **Buffer 3** | 空闲 | [ 等待下一轮循环 ] |
然后你就轮流一块一块轮流读，摄像头通过dma直接往需要写入的已经被读完的内存块里写。
### 块设备
能够随机读写某个块想读什么就读什么，直接读写硬盘的扇区，读出的是16进制数据，因为没有文件系统所以没有意义
brw-rw----  1 root disk    259,    0 Mar 30 16:32 nvme0n1
### 文件或硬链接
-rw-rw----+ 1 cannian Users 107 Mar 31 18:22 xxx

## VFS
在这里我们看到了具体的路径，VFS在硬盘里把ext4里的inode取出来，一个个拼到内存里的VFS路径，还有其他的网卡，摄像头，socket各种io设备全部通过驱动变成一个个inode放在/dev的路径下面， 连在内存里跑着的进程都在这里变成了inode

## fd(文件描述符)
这个是对应用程序最接近的地方
### open
当进程调用系统调用open(<path>)的时候，内核会查到这个路径的inode，并且生成一个`struct file`，这个文件结构体，他里面存这这个路径的inode，offest(偏移量)，还有读写标记位。然后把fd返回给进程，他会给这个进程创建一个表`files_struct`，存着fd和struct file的映射。之后就通过内核给你的fd来对文件进行操作就行了。这个fd-文件结构体的表大致长这样：
- 进程 A 的files_struct：
  - fd : struct file
  - `0`: 标准输入
  - `1`: 标准输出
  - `2`: 标准错误
  - `3`: 刚刚open的那个struct file
这个0、1、2是不是很眼熟，当你想把输出重定向到其他地方基本上都有这一步。
### read
你拿着open返回来的fd数字，然后发起`read(3, buffer, 1024)`的系统调用，就是说在fd是3对应的文件下，接着读1024个字节放到buffer里，然后就去inode里找到他的`Block Map(数据块索引)`[^1]就找到真正的二进制数据的位置了，然后磁盘驱动
通过dma直接把这1024个字节的数据从硬盘里放到内存里的`Page Cache(页缓存)`里，之后再把数据从内核空间拷贝到用户空间里进程的buffer[^2]，再更新offest增加1024，之后再读会从1024开始读。这个offest不会超过Inode里size的大小，不然就读到别的块上了。

## 其他
### iSCSI和reclone
iSCSI是从物理硬盘入手，直接模拟成在/dev里的物理网卡，需要进行分区、文件系统和挂载，reclone是直接在文件系统模拟成具体文件的
### 硬连接
```bash
ln <TARGET> <LINK_NAME>
```
把被链接的目标inode放到了另一个`目录`的inode数据块下面了，这就代表着这一个inode被两个目录的数据块同时引用了。此时一个Inode被两个目录引用，他的Link就从1变成了2。当Link变成0的时候Inode就彻底和系统失联了，导致了物理数据也失联了，他们俩就都变成了硬盘上的一个散沙，不知道什么时候会被覆盖掉。但是如果进程的fd把这个文件加载着了，其实还是能把他从硬盘里拽回来的[^3]

### 软连接
```bash
ln -s
```
新开一个inode数据块里的内容就是被链接的路径，并不是共享inode

[^1]:ll,stat都不会把Inode的所有的信息告诉你，比如硬盘块号，你可以通过filefrag命令来找到他的具体的物理偏移和逻辑偏移。现在的文件系统很聪明，一个文件的物理存储模式分成很多种情况，不一定是一个文件占据了很多连续块，可能分散在硬盘的各个角落
[^2]:sqlite这种使用的mmap零拷贝，直接把修改进程页表让进程的虚拟内存直接连接上page cahe的物理内存上,以获取更高的性能。
[^3]:[详见](https://blog.cannian.space/posts/2026-3-14-ops)