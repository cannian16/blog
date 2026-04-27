---
title: python 面向对象
published: 2026-04-15
description: '关于python的面向对象运行机制和设计模式'
image: ''
tags: ['python','OO']
category: '语言和框架'
draft: false
lang: ''
---
对象/实例：是流水线上的产品。类：是生产产品的模具。模块：是存放模具和产品的车间。

面向对象(Object-Oriented)我们都很熟悉，学校里都学过，我们定义了一个类，这个类就是一个模板，以这个类为蓝图可以创建一大堆不同的对象/实例。面向对象的基本概念，什么继承、多态、接口啥的这些车轱辘话翻来覆去就那样。
我这里先来一个最经典的，类和实例吧。
```bash
In [1]: class Student():
   ...:     ClassName = "学生"
   ...:     def __init__(self, name:str, age : int):
   ...:         self.age = age
   ...:         self.name = name
   ...: 

In [2]: zhang_sang = Student(name="张三", age=10)

In [3]: li_si = Student(name="李四", age=11)
```
# 万物皆对象
python的面向对象要比java的彻底的多。以至于int，str，list，tuple，dict这些初始的数据类型，他们其实也都只是一个类而已。
```bash
In [14]: "a".__class__
Out[14]: str

In [15]: (1).__class__
Out[15]: int

In [16]: [1,2,3].__class__
Out[16]: list

In [17]: (1,2,3).__class__
Out[17]: tuple

In [18]: {"a":1,"b":2,"c":3}.__class__
Out[18]: dict

In [19]: "abc".upper() #如果"abc"不是对象的话怎么能调用upper()方法呢
Out[19]: 'ABC'
```
甚至连类本身都是一个对象

# __变量
大家一般叫他Dunder（即 **D**ouble **Under**score ）,这个是python面向对象的核心中的核心，这里都是这个对象和python解释器的一些协议。理论上来说其实__变量和普通的变量是平等的，只是python解释器选择了这样的变量承担了一些更特殊的任务。
## [鸭子类型](https://zh.wikipedia.org/zh-cn/%E9%B8%AD%E5%AD%90%E7%B1%BB%E5%9E%8B)
**“如果它走起来像鸭子，叫起来也像鸭子，那它就是鸭子。”**

python的Dunder就是非常典范的鸭子类型的实现。他不像是java，验证是不是这个类，必须要是这个类或者是他的子类，其他的全部拒绝。python比如说for i in <可迭代的实例>，他不看你这个类到底是什么，只要你有__iter__()方法你就可以迭代，他不看你到底是什么类型的，甚至python里一个实例可以通过修改__class__来让这个实例瞬间切换身份，指向另一个类的地址，身份不重要，重要的是你的行为。看着像，吃着像，闻着像，那这就是一样的东西。
```bash
In [24]: class Student():
    ...:     def __init__(self, name: str, age: int):
    ...:         self.age = age
    ...:         self.name = name
    ...: 
    ...:     def __iter__(self):
    ...:         yield self.name
    ...:         yield self.age
In [25]: for i in zhang_sang:
...:     print(i)
张三
10
In [32]: iter=li_si.__iter__()#获取一个李四的iter迭代器对象
In [33]: iter.__next__()#然后反复调用这个迭代器的__next__方法
Out[33]: '李四'
In [34]: iter.__next__()
Out[34]: 11
In [43]: li_si.__class__
Out[43]: __main__.Student #这个Student前面为什么有个__main__，为什么不像int，str一样直接输出，可以思考一下，之后讲到模块加载方式的时候就明白了
In [44]: class Dog:
    ...:     def __init__(self):
    ...:         pass
    ...:     def bark(self):
    ...:         print("w")

In [45]: li_si.__class__=Dog 

In [46]: li_si.bark()
w
In [47]: li_si.__class__
Out[47]: __main__.Dog
```
## 全局视野
```python
In [3]: zhang_sang.__dict__
Out[3]: {'name': '张三', 'age': 10}
In [4]: zhang_sang.__dict__.__class__ #可以看出这个字段就是个普通字典
Out[4]: dict
In [5]: zhang_sang.__class__
Out[5]: __main__.Student
```
可以发现对象本身其实不带着这种类方法或者类的变量，对象只带着__class__来找到自己这个类的方法，这也就是为什么上面可以改__class__来更改他的类型来调用别的类的方法。其实挺合理的，不然每个类都带一遍方法会太占用内存了。
其实java也是一样的，方法被放到方法区里，实例放堆内存里调用方法的同一个方法，只不过python没有类和对象的区别，类本身也是对象，统一全放到堆内存里被统一GC(垃圾回收)，通过__class__来牵连起类和对象
```python
In [6]: zhang_sang.__class__.__dict__
Out[6]:  
mappingproxy({'__module__': '__main__',
              'ClassName': '学生',
              '__init__': <function __main__.Student.__init__(self, name: str, age: int)>,
              '__dict__': <attribute '__dict__' of 'Student' objects>,
              '__weakref__': <attribute '__weakref__' of 'Student' objects>,
              '__doc__': None})
```
python里一切的包括类，数字，字符串，列表，元组其实都是type的实例。
```python

In [14]: "a".__class__.__class__
Out[14]: type

In [15]: zhang_sang.__class__.__class__
Out[15]: type

In [16]: (1).__class__.__class__
Out[16]: type

In [17]: (1,).__class__.__class__
Out[17]: type

In [23]: list.__class__
Out[23]: type

In [24]: Student.__class__
Out[24]: type

In [25]: type.__dict__
Out[25]: 
mappingproxy({'__new__': <function type.__new__(*args, **kwargs)>,
              '__repr__': <slot wrapper '__repr__' of 'type' objects>,
              '__call__': <slot wrapper '__call__' of 'type' objects>,
              '__getattribute__': <slot wrapper '__getattribute__' of 'type' objects>,
              '__setattr__': <slot wrapper '__setattr__' of 'type' objects>,
              '__delattr__': <slot wrapper '__delattr__' of 'type' objects>,
              '__init__': <slot wrapper '__init__' of 'type' objects>,
              '__or__': <slot wrapper '__or__' of 'type' objects>,
              '__ror__': <slot wrapper '__ror__' of 'type' objects>,
              'mro': <method 'mro' of 'type' objects>,
              '__subclasses__': <method '__subclasses__' of 'type' objects>,
              '__prepare__': <method '__prepare__' of 'type' objects>,
              '__instancecheck__': <method '__instancecheck__' of 'type' objects>,
              '__subclasscheck__': <method '__subclasscheck__' of 'type' objects>,
              '__dir__': <method '__dir__' of 'type' objects>,
              '__sizeof__': <method '__sizeof__' of 'type' objects>,
              '__basicsize__': <member '__basicsize__' of 'type' objects>,
              '__itemsize__': <member '__itemsize__' of 'type' objects>,
              '__flags__': <member '__flags__' of 'type' objects>,
              '__weakrefoffset__': <member '__weakrefoffset__' of 'type' objects>,
              '__base__': <member '__base__' of 'type' objects>,
              '__dictoffset__': <member '__dictoffset__' of 'type' objects>,
              '__name__': <attribute '__name__' of 'type' objects>,
              '__qualname__': <attribute '__qualname__' of 'type' objects>,
              '__bases__': <attribute '__bases__' of 'type' objects>,
              '__mro__': <attribute '__mro__' of 'type' objects>,
              '__module__': <attribute '__module__' of 'type' objects>,
              '__abstractmethods__': <attribute '__abstractmethods__' of 'type' objects>,
              '__dict__': <attribute '__dict__' of 'type' objects>,
              '__doc__': <attribute '__doc__' of 'type' objects>,
              '__text_signature__': <attribute '__text_signature__' of 'type' objects>,
              '__annotations__': <attribute '__annotations__' of 'type' objects>,
              '__type_params__': <attribute '__type_params__' of 'type' objects>})
```
在java中，一个对象必须从一个类里new出来，但是在python中，对象才是一切，类只是对象的一种形态，继承其实和类的实例化没有任何区别，一个类本身就是父类的一个实例。
## __class__
对象里的__class__属性就是实现这个对象的类，由于类本身就是父类的对象，所以所有的实例最总都会回溯到`type`。这个是每个对象都一定会有的，甚至连list，int，str这种都有。属性的普及率100%，python里一切的底层骨架，背后是c结构体里的一个指针，一切链接的基础。
可以用这个来看实例的类型，比如：
```python
In [11]: Student.__init__.__class__
Out[11]: function
```
## “仓库型”属性
这个__dict__属性就是一个dict字典对象，字典的本质就是个哈希表。__dict__就是命名空间本身，dir()和__dict__是一样的

为了性能int，str这种基础设施和别的类不一样而且本来就不需要__dict__，所以没有，但是别的对象一般都是有的，你定义的类里面的一切包括，方法，属性等等一切都会存在在__dict__的字典里。实例的__dict__实例字典和类的__dict__类字典有些不同，实例字典允许随意修改，增加减少字段，但是类字典只能通过python暴露的反射函数来修改类字典,比如`setattr(obj, "name", value)`
## “契约型”属性
这种属性需要初始化成方法对象，给解释器提供**钩子**，让代码里的str()、for i in <对象>、()这个东西是调用这个函数对象的意思，必须要实现__call__才能被()调用。

- __init__(function)：实现了这个才能用`<类名>()`来初始化实例
- __iter__(function)：实现了这个才能作为迭代器去使用
- __call__(function)：实现了这个才能被当函数调用，函数本身也是个对象
- __str__(function)：实现了这个才能被str(),print()转换成字符串
- __getitem__(function)：
- __add__(function)：实现了这个可以让你的对象使用`+`来进行两个对象的运算，str的相加就是这个道理。
## “元数据型”属性
- __doc__(str/None)：文档字符串（注释）
- __name__(str)：类或函数的真名。
- __mro__(tuple)：继承搜索的顺序表。
- __module__(str)：这个对象是在哪个模块里定义的。
- __file__(str)：这个模块的文件路径

# 启动与加载
当python解释器启动时，无论是使用交互式，还是直接python启动模块，首先解释器会初始化第一个模块对象`__main__`，并把启动的模块的所有指令全部放进去。当__main__载入到了一个import指令，就比如`import httpx`，首先他会先在__main__的__dict__也就是命名空间里创建一个httpx模块。
也就是说只有直接被启动的模块，他的__name__会被重写成__main__，如果是被import的那么就是直接使用原本的模块名当__name__，正因如此，所以如果你想要让一个模块只有在被直接启动的时候才进行一些操作就要用，很经典的`if __name__ == "__main__"`
```python
import __main__#把当前的主模块自己导入自己了
In [43]: __main__.__main__.Student #甚至可以无限的循环引用，因为__main__本身也被加入到了__main__的__dict__里了
Out[43]: __main__.Student
```
## 模块
模块本身也是一个对象，是python加载代码到内存的最小单位，而且解释器确保每个模块只会被加载一次。加载的那一下会顺序执行该文件中的所有指令。因为模块的这个只会被加载一次的特性，所以模块本身就是一个单例
## 单例和多例
我们先进行一个实验
```py
# 首先我们创建一个test.py
class A:#这里定义了一个类A
    def __init__(self, b):
        self.b = b
# 我们在同一个模块下把这个类A，进行实例化
TestCLass = A("test")
```
接下来直接用解释器去体验一下
```bash
In [1]: import test

In [2]: a = test.TestCLass

In [3]: a.b
Out[3]: 'test'

In [4]: b=test.TestCLass

In [5]: b.b
Out[5]: 'test'

In [6]: a.b = 1

In [7]: b.b
Out[7]: 1
#感受到了吗，python的单例
#下面尝试一下普通的多例
In [8]: c=test.A("ccc")

In [9]: d=test.A(111)

In [10]: c.b
Out[10]: 'ccc'

In [11]: d.b
Out[11]: 111
```
大部分人的面向对象基本上都是从java做起的，看起来python里的__init__方法就和java的里的构造方法很像，还有调用这个__init__类看起来就像是new一个对象一样的，python的面向对象本身其实和java如出一辙，神来之笔在于python模块的加载机制。
java你想实现单例通常需要用到静态内部类来实现全局的共享的单例，就像下面
```java
public class PanClient {
    private static final PanClient instance = new PanClient(); //在内部初始化一个自身的实例变量
    private PanClient() {} // 首先就是要禁止外面new他，不然肯定不是单例了
    public static PanClient getInstance() { return instance; }//对外只暴露一个获取这个内部对象的方法，这样就做到了全局单例了
}
```
但是python设计导入时，一个模块被确保只加载一次，当import第一次模块的时候，python发现模块还没有在内存中，python把里面的东西全部加载到内存中，之后别的也使用使用到了这个模块,python发现内存里已经有了，就会被链接到同一个内存的区域，所以同一个进程，无论是谁使用了test.TestCLass都是共享的同一个实例。
### 更高层次的单例
但是我们有的时候希望跨进程间有一个单例，但是内存页表我们物理上就突破不了，没办法让两个进程import的模块在内存中指向同样的地方。但是我们可以取巧，用redis在内存中放置键值对，在模块的实例中统一从redis的内存中把值给取出来，
这样就办到了虽然不是同一个进程，不是同一个模块，不是同一个实例，但是逻辑上数据的来源却都是从redis内存中取来的

# 反射
这个名字有点奇怪，我感觉上，就像你一般来说用一个对象，都是直接调用的，但是通过反射机制，你可以先自己检查反省一下，这个对象到底有没有这个属性，然后再去调用这个属性。
有些地方会有自省这种表达，我感觉反射的重点在`射`也就是他检查之后还会调用，而自省的重点在`省`也就是只检查有没有但是不调用
就是查对象实例的具体的细节，但是对于python这种自由度，实际上你完全可以不通过官方的反射函数来实现反射，用__dict__和__mro__自己实现一套反射机制完全可行，但是对于java这种的话，有一个官方的反射机制是完全必须的。
| 动作 | 函数 | 作用 |
| :--- | :--- | :--- |
| **查** | `hasattr(obj, "name")` | 查对象有没有这个属性 |
| **拿** | `getattr(obj, "name", default)` | 获取对象的一个属性 |
| **改** | `setattr(obj, "name", value)` | 给对象添加一个属性 |
| **删** | `delattr(obj, "name")` | 把对象里的属性删了 |

# 不要对象
似乎在python里一切都是对象，所有的一切，都是虚的，连print、+、for都是通过对象实现的。但是实际上最终真实的只有极少数的，真实的：
- 赋值(`=`)
- 分支与循环(`if`,`while`)
- 函数定义和调用(`def`,`()`)
- 逻辑运算(`and`、`or`、`not`)
这些是真的对应着真实的机器码里的操作码。看起来庞大的系统实际上真实的只有那么一点点，剩下的高级功能全部是通过**命名契约**来实现的，契约就是那么多的Dunder，通过他几乎可以修改python里的一切。

# 结语
约定的重量是如此之大，能量是如此之强，高度发达的文明离不开契约精神。python的设计哲学似乎与卢梭在《社会契约论》中探讨的契约精神惊人的一致。从这个角度来看java就像是封建强权一样，通过检查你的出生类型，强制的来让大规模的系统有序，或许这就是为啥java的`班味`看起来总是很重。而python似乎是更自由，更平等的设计，“我不在乎你是谁，我只在乎你是否履行了契约规定的义务。”内核的精简和权力的下放，正是因为这样的设计才让python的第三方生态如此之繁荣。在更大的维度，整个互联网也是通过，api的契约，你相信api能传回你需要的字段，你可以很方便的集成到你的项目组里。大到整个社会也是契约精神无处不在，契约就是人类社会对抗大规模协作熵增的利器。