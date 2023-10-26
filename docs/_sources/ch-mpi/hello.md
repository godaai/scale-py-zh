# MPI Hello World

## 通信模式

MPI 提供的能力更加底层，对于通信模式，通常有两种：双边和单边。

* 双边：通信双方均同意数据的收发。发送进程调用发送函数，接收进程调用接收函数。
* 单边：一方远程读或者写另一方的数据，一方无需等待另一方。

```{figure} ../img/ch-mpi/communications.svg
---
width: 600px
name: ray-ecosystem
---
两种通讯模式：双边和单边
```

## World 和 Rank

在进行 MPI 编程时，进程之间要互相通信，我们首先要解决两个问题：在 MPI 的众多进程中，“我是谁？”，除了我，“还有谁？”。 `MPI_Comm_rank` 定义了我是谁。`MPI_COMM_WORLD` 定义了还有谁的问题。 开始一个 MPI 程序时，要先定义一个 World，这个世界里有 `size` 个进程，每个进程有一个识别自己的号码，这个号码被称为 Rank，Rank 是 0 到 `size - 1` 的整数。更严肃地阐述：

* MPI 中的 World 是指所有参与并行计算的进程的总集合。在一个 MPI 程序中，所有的进程都属于一个默认的通信域，这个通信域就被称为 `MPI_COMM_WORLD`。所有在这个通信域中的进程都可以进行通信。
* World 中的每个进程都有一个唯一的 Rank，Rank 用来标识进程在通信域中的位置。由于每个进程有自己的 Rank 号码，那在编程时，可以控制，使得 Rank 为 0 的进程发送数据给 Rank 为 1 的进程。

```python
from mpi4py import MPI


comm = MPI.COMM_WORLD

print(f"Hello! I'm rank {comm.Get_rank()} of {comm.Get_size()} running on host {MPI.Get_processor_name()}.")

comm.Barrier()
```

如果在笔记本上，启动 8 个进程，在命令行中执行：

```bash
mpirun -n 8 hello.py
```

