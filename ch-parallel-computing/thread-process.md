(sec-thread-process)=
# 线程和进程

CPU、GPU、网卡等都是硬件层面上的概念，在软件层面，经常使用线程（Thread）或进程（Process）来描述程序的运行过程。

## 进程与线程

CPU、GPU、网卡等都是被操作系统（Operating System，OS）管理的。操作系统一方面管理硬件，另一方面通过各类应用软件为用户提供服务。正在运行的软件就是进程（Process）。以个人的笔记本电脑为例，使用浏览器浏览网页时，操作系统创建了一个浏览器的进程；使用文本编辑软件 Word 编写文字内容时，操作系统创建了一个 Word 进程。macOS 上的**活动监视器**（如 {numref}`fig-mac-process` 所示），和 Windows 上的**任务管理器**，都可以看到操作系统当前运行的进程，以及各个进程对 CPU、内存等资源的占用。

```{figure} ../img/ch-parallel-computing/mac-process.png
---
width: 600px
name: fig-mac-process
---
macOS 的活动监视器
```

技术层面上，操作系统管理所有进程的执行，给进程们合理地分配资源：操作系统以进程为单位分配主存空间，每个进程都有自己的主存地址空间、数据栈等等。

大部分编程语言实现时，一个进程包含多个线程，如 {numref}`fig-process-thread` 所示。每个线程运行在一个物理计算核心上，一个进程的多个线程可利用多个物理计算核心。

```{figure} ../img/ch-parallel-computing/process-thread.svg
---
width: 600px
name: fig-process-thread
---
进程和线程
```

从 {numref}`fig-process-thread` 看到，一个进程拥有多个并发的执行线程。多个线程共享相同的上下文（数据、文件等），线程间的数据共享和通信更加容易。

进程之间是相互隔离的，如果多个进程之间要交换数据，必须通过进程间通信机制（Inter-Process Communication，IPC）来实现数据共享，比如多个进程共享内存（`multiprocessing.shared_memory`）或者 {numref}`sec-mpi-intro` 将要介绍的消息传递接口（Message Passing Interface，MPI）。

## 线程安全

由于多个线程共享了上下文（data、files 等），不同线程访问同样数据时，容易产生**线程安全**（Thread Safe）问题。以这段代码顺序执行为例：

```
x = x + 1
x = x * 2
x = x - 1
```

如果这三行计算被调度到三个线程上，数据 `x` 是被三个线程共享的，三个线程的执行顺序将严重影响计算的结果。{numref}`fig-thread-safe` 展示了三种不同的时序可能性，三种时序的计算结果可能各有不同。由于调度时序因素导致的问题，会使得并行计算的结果不符合预期，线程不安全。

```{figure} ../img/ch-parallel-computing/thread-safe.svg
---
width: 600px
name: fig-thread-safe
---
线程安全
```

解决线程安全的最简单办法是加锁。如 {numref}`fig-thread-lock` 所示，对于共享的数据，每个线程对其进行修改前先加锁，修改完后再释放锁。

```{figure} ../img/ch-parallel-computing/thread-lock.svg
---
width: 600px
name: fig-thread-lock
---
线程锁
```

## 全局解释器锁

Python 解释器 CPython 在解决线程安全时使用了一个激进的方式：全局解释器锁（Global Interpreter Lock，GIL）。

:::{note}
CPython 是 Python 解释器的一种实现，也是使用最广泛的一种实现。CPython 主要使用 C 语言实现。我们使用 Anaconda 安装的 Python 就是 CPython。

除了 CPython，还有 Jython，使用Java 实现；IronPython 使用 C# 实现。
:::

GIL 全局解释器锁使得 Python 一个进程下只允许一个线程在运行。GIL 下，一个 Python 进程只能有一个线程运行，也只能利用一个 CPU 核心。GIL 的优势之一就是线程安全；缺点也很明显，在现代单机多核计算机上，Python 以及大部分库比如 NumPy、pandas、scikit-learn 的很多功能只能利用一个核心。

GIL 与整个 Python 生态紧密绑定，它与 NumPy、pandas 等很多库息息相关，移除 GIL 可谓牵一发而动全身。所以，想让 Python 充分利用现代计算机的多核，其实并不那么容易。幸运的是，Python 官方正在解决这个问题，不久的将来，CPython 将移除 GIL。