(multi-core-cluster-heterogeneous-computing)=
# 现代计算机体系结构

大数据与人工智能应用对算力要求极高，为应对飞速增长的算力需求，芯片与硬件厂商近年来重点发展多核、集群（Cluster）和异构计算（Heterogeneous Computing）。{numref}`computer-arch` 展示了现代计算机的体系结构。

```{figure} ../img/ch-intro/computer-arch.svg
---
width: 600px
name: computer-arch
---
现代计算机体系结构示意图
```

所谓多核指的是一台计算机上有多颗中央处理器（Central Processing Unit，CPU），每个 CPU 有多个计算核心（Core）。CPU 内部有自己的缓存，比如一级缓存（Level 1 Cache，L1 Cache）或二级缓存（Level 2 Cache，L2 Cache），CPU 外部有主存（Main Memory）。

所谓集群指多台计算机通过高速网络互联，每台计算机上都配置了网卡（Network Interface Card，NIC）。

近年来，以 GPU 为代表的异构计算异军突起，成为人工智能算力核心。异构计算指在 CPU 芯片微架构（Microarchitecture）基础上，引入图形处理器（Graphics Processing Units），现场可编程门阵列（Field Programmable Gate Array，FPGA）等另一套芯片微架构。其中，CPU 仍然负责传统的处理和调度，GPU 等设备被用来加速某些特定的任务，比如图形图像、人工智能、区块链等。

## CPU

现代 CPU 通常有多个计算核心，比如，笔记本电脑和台式机最多可拥有十几个计算核心，数据中心服务器高达上百个核心。然而，如何让计算任务分布到多个核心上并不简单，需要程序员在编写软件时将计算任务合理地调度到不同核心上。

## 网卡

单台计算机的计算能力有限，为搭建一个高速互联的集群，数据中心服务器之间通常配置了高速网络，比如 RoCE（RDMA over Converged Ethernet）或 InfiniBand。每台计算机上配有至少一块高速网卡，多台计算机之间通过光纤互联，以获得极低的延迟和极高的吞吐率。这样不同节点之间的通信就像在单个节点上进行计算一样。

## 异构计算

在异构计算的框架下，CPU 和主存通常被称为主机（Host），各类专用的加速器被称为设备（Device）。尽管异构计算是一个很宽泛的概念，但当前基于 GPU 的异构计算是主流，尤其是以英伟达为代表的 GPU 占据了大量市场份额，所以这里主要以 GPU 为例介绍异构计算。GPU 有区别于 CPU 的芯片微架构和编译软件栈。软件层面，英伟达的 GPU 提供了 CUDA（Compute Unified Device Architecture）编程接口，硬件层面，GPU 有很多个专用计算核心（CUDA Core）和 GPU 上的存储。通常，数据从主存到 GPU 存储之间搬运有一定成本。其他加速器与英伟达 GPU 整体结构也很相似。

## 顺序执行与并行执行

如果不对计算任务（Task）进行并行加速，大部分计算任务是顺序执行的，即 {numref}`serial-timeline` 所示。这里的 Worker 可以是一个计算核心，也可以是集群中的一个节点。

```{figure} ../img/ch-intro/serial-timeline.png
---
name: serial-timeline
---
顺序执行的时间轴示意图
```

集群和异构计算提供了更多可利用的计算核心，并行计算将计算任务分布到多个 Worker 上，如 {ref}`distributed-timeline` 所示。无论是在单机多核编程，还是在集群多机，都需要一个调度器（Scheduler）将计算任务分布到不同的 Worker 上。

```{figure} ../img/ch-intro/distributed-timeline.svg
---
name: distributed-timeline
---
分布式执行的时间轴示意图
```