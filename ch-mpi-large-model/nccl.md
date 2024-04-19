# NCCL 简介

随着 GPU 被广泛应用高性能计算各个领域，尤其是深度学习和大模型对延迟和带宽要求越来越高，如何在多个 GPU 之间高效传输数据愈发重要。GPU 编程中，数据需要从 CPU 和 GPU 之间相互拷贝，而 MPI 最初为 CPU 集群设计，无法适应大规模 GPU 集群的场景。比如，传统的 MPI 是进程间数据传输，而单台 GPU 服务器通常有多张 GPU 卡，单机多卡之间也要进行大量数据传输。又比如 {numref}`fig-mpi-wo-gpu-direct` 中，多个节点之间的 GPU 通信要经过以下步骤：数据从 GPU 拷贝到 CPU，再通过 MPI 相互发送数据。为了适应大规模 GPU 集群和深度学习应用，英伟达设计了英伟达集合通讯库（NVIDIA Collective Communications Library，NCCL），旨在解决 MPI 在大规模 GPU 集群上无法完成的各类问题。

```{figure} ../img/ch-mpi-large-model/mpi-wo-gpu-direct.svg
---
width: 800px
name: fig-mpi-wo-gpu-direct
---
先将数据从 GPU 拷贝到 CPU，再进行通信
```

MPI 与 NCCL 并不是完全是替代关系，NCCL 的很多通信原语，比如点对点通信和集合通信都借鉴了 MPI，可以说 NCCL 是在 MPI 基础上做的延展，更适合 GPU 集群。{numref}`fig-gpu-communication` 展示了 NCCL 实现的通信原语。

```{figure} ../img/ch-mpi-large-model/gpu-communication.svg
---
width: 800px
name: fig-gpu-communication
---
NCCL 实现了常见的通信原语
```

同样，其他加速器厂商也提出了自己的通信库，比如：

* AMD 提供了针对 ROCm 的 RCCL（ROCm Communication Collectives Library）
* 华为提供了 HCCL（Huawei Collective Communication Library）
  

这些集合通信库都是针对特定硬件的通信库，旨在解决特定集群的通信问题。

NCCL 主要提供了 C/C++ 编程接口，Python 社区如果使用的话，可以考虑 PyTorch 的 `torch.distributed`。NCCL 也是 PyTorch 推荐的 GPU 并行计算后端。本书不再细致讲解 `torch.distributed` 的使用，而是继续用 MPI 来演示大模型训练和推理过程中涉及的各类通信问题。