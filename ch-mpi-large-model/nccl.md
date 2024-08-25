# NCCL 简介

随着 GPU 在高性能计算领域的广泛应用，尤其是在深度学习和大型模型训练中，对延迟和带宽的要求日益严格，因此，实现多个 GPU 之间高效的数据传输变得越发重要。在 GPU 编程中，数据经常需要在 CPU 和 GPU 之间进行复制。然而，MPI 最初是为 CPU 集群设计的，并不完全适应大规模 GPU 集群的应用场景。
例如，在传统的 MPI 中，数据传输是在进程间进行的。但在单机多 GPU 服务器上，通常需要在多张 GPU 卡之间进行大量的数据传输。如 {numref}`fig-mpi-wo-gpu-direct` 所示，多个节点上的 GPU 通信需要经过以下步骤：首先将数据从 GPU 复制到 CPU，然后通过 MPI 进行数据的发送和接收。为了更好地适应大规模 GPU 集群和深度学习应用的需求，NVIDIA 设计了 NVIDIA 集合通信库（NVIDIA Collective Communications Library， NCCL），它旨在解决 MPI 在大规模 GPU 集群上遇到的各种问题。

```{figure} ../img/ch-mpi-large-model/mpi-wo-gpu-direct.svg
---
width: 800px
name: fig-mpi-wo-gpu-direct
---
先将数据从 GPU 拷贝到 CPU，再进行通信
```

MPI 与 NCCL 并不是完全的替代关系。NCCL 的许多通信原语，例如点对点通信和集合通信，都受到了 MPI 的影响。可以说，NCCL 是在 MPI 的基础上进行的扩展，它更加适合 GPU 集群环境。{numref}`fig-gpu-communication` 展示了 NCCL 实现的通信原语。

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
  
这些集合通信库是为特定硬件量身定制的，目的是解决特定集群环境中的通信挑战。

NCCL 主要提供 C/C++ 编程接口。对于 Python 社区的开发者，如果需要使用 NCCL，可以考虑 PyTorch 的 `torch.distributed` 库。NCCL 也是 PyTorch 推荐的 GPU 并行计算后端。本书不会深入讲解 `torch.distributed` 的使用细节，而是继续使用 MPI 来展示大模型训练和推理过程中涉及的各种通信问题。