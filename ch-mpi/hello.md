(mpi-hello-world)=
# MPI Hello World

## 通信模式

MPI 提供的能力更加底层，对于通信模式，通常有两种：双边和单边。

* 双边（Cooperative）：通信双方均同意数据的收发。发送进程调用发送函数，接收进程调用接收函数。
* 单边（One-sided）：一方远程读或者写另一方的数据，一方无需等待另一方。

```{figure} ../img/ch-mpi/communications.svg
---
width: 600px
name: mpi-communications
---
两种通讯模式：双边和单边
```

## World 和 Rank

在进行 MPI 编程时，进程之间要互相通信，我们首先要解决两个问题：在 MPI 的众多进程中，“我是谁？”，除了我，“还有谁？”。 `MPI_Comm_rank` 定义了我是谁。`MPI_COMM_WORLD` 定义了还有谁的问题。 开始一个 MPI 程序时，要先定义一个 World，这个世界里有 `size` 个进程，每个进程有一个识别自己的号码，这个号码被称为 Rank，Rank 是 0 到 `size - 1` 的整数。更严肃地阐述：

* MPI 中的 World 是指所有参与并行计算的进程的总集合。在一个 MPI 程序中，所有的进程都属于一个默认的通信域，这个通信域就被称为 `MPI_COMM_WORLD`。所有在这个通信域中的进程都可以进行通信。
* World 中的每个进程都有一个唯一的 Rank，Rank 用来标识进程在通信域中的位置。由于每个进程有自己的 Rank 号码，那在编程时，可以控制，使得 Rank 为 0 的进程发送数据给 Rank 为 1 的进程。

## 案例：Hello World

下面使用一个简单的例子来演示 MPI 编程。

```python
from mpi4py import MPI


comm = MPI.COMM_WORLD

print(f"Hello! I'm rank {comm.Get_rank()} of {comm.Get_size()} running on host {MPI.Get_processor_name()}.")

comm.Barrier()
```

在这段程序中，`print` 是上单个进程内执行的，打印出当前进程的 Rank 和主机名。`comm.Barrier()` 将每个进程做了阻断，直到所有进程执行完毕后，才会进行下面的操作。本例中，`comm.Barrier()` 后无其他操作，程序将退出。

如果在个人电脑上，启动 8 个进程，在命令行中执行：

```bash
mpirun -np 8 python hello.py
```

`mpirun` 其实不是 MPI 标准的一部分，所以不同厂商的 `mpirun` 的参数会有一些区别。`mpirun` 命令在有的实现中等同于 `mpiexec`。相比 C/C++ 或 Fortran，mpi4py 的方便之处在于不需要使用 `mpicc` 编译器进行编译，直接执行即可。

如果有一个集群，且集群挂载了一个共享的文件系统，即集群上每个节点上的特定目录的内容是一样的，`hello.py` 和 `mpirun` 是一模一样的。可以这样拉起：

```bash
mpirun –hosts h1:4,h2:4,h3:4,h4:4 –n 16 python hello.py
```

这个启动命令一共在 16 个进程上执行，16 个进程分布在 4 个计算节点上，每个节点使用了 4 个进程。如果节点比较多，还可以单独编写一个节点文件，比如命名为 `hf`，内容为：

```
h1:8
h2:8
```

这样执行：

```
mpirun –hostfile hf –n 16 python hello.py
```

## Communicator

刚才我们提到了 World 的概念，并使用了 `MPI_COMM_WORLD`，更准确地说，`MPI_COMM_WORLD` 是一个 Communicator。MPI 将进程划分到不同的组（Group）中，每个 Group 有不同的 Color，Group 和 Color 共同组成了 Communicator，或者说 Communicator 是 Group + Color 的名字，一个默认的 Communicator 就是 `MPI_COMM_WORLD`。

对于一个进程，它可能在不同的 Communicator 中，因此它在不同 Communicator 中的 Rank 可能也不一样。如 {numref}`mpi-communicatitor` 所示，每一层可以理解为一个 Communicator，圆圈中的数字是进程在这个 Communicator 中的 Rank，每一层的进程通信是相互独立的。

```{figure} ../img/ch-mpi/communicators.png
---
width: 800px
name: mpi-communicatitor
---
Communicators
```