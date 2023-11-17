(mpi-point2point)=
# 点对点通信

一个最简单的通信模式点对点（Point-to-Point）通信，点对点通信又分为阻塞式（Blocking）和非阻塞式（Non-Blocking）。实现点对点时主要考虑两个问题：

* 如何控制和识别不同的进程？比如，想让 Rank 为 0 的进程给 Rank 为 1 的进程发消息。
* 如何控制数据的读写？多大的数据，数据类型是什么？

## 发送与接收

[`Comm.send`](https://mpi4py.readthedocs.io/en/latest/reference/mpi4py.MPI.Comm.html#mpi4py.MPI.Comm.send) 和 [`Comm.recv`](https://mpi4py.readthedocs.io/en/latest/reference/mpi4py.MPI.Comm.html#mpi4py.MPI.Comm.recv) 分别用来阻塞式地发送和接收数据。

`Comm.send(obj, dest, tag=0)` 的参数主要是 `obj` 和 `dest`。`obj` 就是我们想要发送的数据，数据可以是 Python 内置的数据类型，比如 `list` 和 `dict` 等，也可以是 NumPy 的 `ndarray`，甚至是 GPU 上的 cupy 数据。上一节 {ref}`mpi-hello-world` 我们介绍了 Communicator 和 Rank，可以通过 Rank 的号码来定位一个进程。`dest` 可以用 Rank 号码来表示。`tag` 主要用来标识，给程序员一个精细控制的选项，使用 `tag` 可以实现消息的有序传递和筛选。接收方可以选择只接收特定标签的消息，或者按照标签的顺序接收消息，以便更加灵活地控制消息的发送和接收过程。

## 案例1：发送 Python 对象

比如，我们发送一个 Python 对象。Python 对象在通信过程中的序列化使用的是 [pickle](https://docs.python.org/3/library/pickle.html#module-pickle)。

```python
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

if rank == 0:
    data = {'a': 7, 'b': 3.14}
    comm.send(data, dest=1)
    print(f"Sended: {data}, from rank: {rank}.")
elif rank == 1:
    data = comm.recv(source=0)
    print(f"Received: {data}, to rank: {rank}.")
```

在命令行中这样启动：

```bash
mpiexec -np 2 python send-py-object.py
```

## 案例2：发送 NumPy `ndarray`

或者发送一个 NumPy `ndarray`，如下：

```python
from mpi4py import MPI
import numpy as np

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

# 明确告知 MPI 数据类型为 int
# dtype='i', i 为 INT 的缩写
if rank == 0:
    data = np.arange(10, dtype='i')
    comm.Send([data, MPI.INT], dest=1)
    print(f"Sended: {data}, from rank: {rank}.")
elif rank == 1:
    data = np.empty(10, dtype='i')
    comm.Recv([data, MPI.INT], source=0)
    print(f"Received: {data}, to rank: {rank}.")

# MPI 自动发现数据类型
if rank == 0:
    data = np.arange(10, dtype=np.float64)
    comm.Send(data, dest=1)
    print(f"Sended: {data}, from rank: {rank}.")
elif rank == 1:
    data = np.empty(10, dtype=np.float64)
    comm.Recv(data, source=0)
    print(f"Received: {data}, to rank: {rank}.")
```

```{note}
这里的 `Send` 和 `Recv` 函数的首字母都大写了，因为大写的 `Send` 和 `Recv` 等方法是基于缓存（Buffer）的。对于这些基于缓存的函数，应该明确数据的类型，比如传入这样的二元组 `[data, MPI.DOUBLE]` 或三元组 `[data, count, MPI.DOUBLE]`。刚才例子中，`comm.Send(data, dest=1)` 没有明确告知 MPI 其数据类型和数据大小，是因为 MPI 对 NumPy 和 cupy `ndarray` 做了类型的自动探测。
```

## 案例3：Master-Worker

现在我们做一个 Master-Worker 案例，共有 `size` 个进程，前 `size-1` 个进程作为 Worker，随机生成数据，最后一个进程（Rank 为 `size-1`）作为 Master，接收数据，并将数据的大小打印出来。

```python
from mpi4py import MPI
import numpy as np

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if rank < size - 1:
    # Worker 进程
    np.random.seed(rank)
    # 随机生成
    data_count = np.random.randint(100)
    data = np.random.randint(100, size=data_count)
    comm.send(data, dest=size - 1)
    print(f"Worker: worker ID: {rank}; count: {len(data)}")
else:
    # Master 进程
    for i in range(size - 1):
        status = MPI.Status()
        data = comm.recv(source=MPI.ANY_SOURCE, status=status)
        print(f"Master: worker ID: {status.Get_source()}; count: {len(data)}")

comm.Barrier()
```

在这个例子中，`rank` 小于 `size - 1` 的进程是 Worker，随机生成数据，并发送出给最后一个进程（进程 Rank 号为 `size - 1`）。最后一个进程接收数据，并打印出接收数据的大小。

## 阻塞 v.s. 非阻塞

### 阻塞

我们先分析一下阻塞式通信。`Send` 和 `Recv` 这两个基于缓存的方法：

* `Send` 直到缓存是空的时候，也就是说缓存中的数据都被发送出去后，才返回（`return`），允许运行用户代码中剩下的业务逻辑。缓存区域可以被接下来其他的 `Send` 循环再利用。
* `Recv` 直到缓存区域数据到达，才返回（`return`），，允许运行用户代码中剩下的业务逻辑。

如 {ref}`mpi-communications` 所示，阻塞通信是数据完成传输，才会返回（`return`），否则一直在等待。

```{figure} ../img/ch-mpi/blocking.svg
---
width: 800px
name: blocking-communications
---
阻塞式通信示意图
```

阻塞式通信的代码更容易去设计，但出现问题是死锁，比如类似下面的逻辑，Rank = 1 的产生了死锁，应该将 `Send` 和 `Recv` 调用顺序互换

```python
if rank == 0:
	comm.Send(..to rank 1..)
    comm.Recv(..from rank 1..)
else if (rank == 1): <- 该进程死锁
    comm.Send(..to rank 0..)       <- 应将 Send Revc 互换
    comm.Recv(..from rank 0..)
```

### 非阻塞

非阻塞式通信调用后直接返回 `Request` 句柄（Handle），程序员接下来再对 `Request` 做处理，比如等待 `Request` 涉及的数据传输完毕。非阻塞式通信有大写的 i（I） 作为前缀， `Irecv` 的函数参数与之前相差不大，只不过返回值是一个 `Request`：`Request = Isend(buf, dest, tag=0`。 `Request` 类提供了 `wait` 方法，显示地调用 `wait()` 可以等待数据传输完毕。用 `Isend` 写的阻塞式的代码，可以改为 `Isend` + `Request.wait()` 以非阻塞方式实现。

```python
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

if rank == 0:
    data = {'a': 7, 'b': 3.14}
    req = comm.isend(data, dest=1, tag=11)
    print(f"Sending: {data}, from rank: {rank}.")
    req.wait()
    print(f"Sended: {data}, from rank: {rank}.")
elif rank == 1:
    req = comm.irecv(source=0, tag=11)
    print(f"Receiving: to rank: {rank}.")
    data = req.wait()
    print(f"Received: {data}, to rank: {rank}.")
```

{numref}`non-blocking-communications` 展示非阻塞通信 `wait()` 加入后数据流的变化。

```{figure} ../img/ch-mpi/non-blocking.svg
---
width: 800px
name: non-blocking-communications
---
非阻塞式通信示意图
```