(sec-pipeline-parallel)=
# 流水线并行

流水线并行是另一种常见的大型模型并行方法。当模型大小没有超过单个 GPU 显存容量时，数据并行通过在每个 GPU 上复制一份模型权重，成为最简单易用的选项。然而，现代的模型已经变得如此庞大，以至于无法放入单块 GPU 中，例如拥有 175B 参数的 GPT-3。即使使用 FP16 格式存储，也需要 350GB 的存储空间，而单块 NVIDIA A100 或 H100 GPU 的显存仅为 80GB。流水线并行提供了解决这一问题的方案，它通过将大模型的不同层分配到不同的 GPU 上来实现。这一核心思想在 {numref}`fig-pipeline-parallel-img` 中有详细展示。

```{figure} ../img/ch-mpi-large-model/pipeline-parallel.svg
---
width: 600px
name: fig-pipeline-parallel-img
---
朴素流水线并行示意图
```

## 朴素流水线并行

假如模型被切分为两部分，第一部分在 GPU 0 上，第二部分在 GPU 1 上。每个 GPU 上计算前向传播和反向传播，如 {numref}`fig-pipeline-parallel-distributed` 所示。

* 前向传播过程中，输出需要在 GPU 之间传输。
* 反向传播过程中，损失对于输出的梯度需要在 GPU 之间传输。

```{figure} ../img/ch-mpi-large-model/pipeline-parallel-distributed.svg
---
width: 600px
name: fig-pipeline-parallel-distributed
---
在两个 GPU 上使用流水线并行
```

在这种最朴素的流水线并行场景，只需要使用点对点通信：`MPI.Send` 和 `MPI.Recv`，不需要集合通信。

朴素流水线并行有一个致命的缺点，那就是**GPU 利用率低**。主要体现在：

* 任何一个时刻只有一块 GPU 在进行计算，其他 GPU 都在等待上下游的计算结果传过来。如果不考虑通信的时间成本，GPU 利用率仅为 $\frac{1}{\# GPUs}\%$。
* 如果考虑通信的时间成本，GPU 在等待网卡的数据传输过来，GPU 计算和 GPU 之间通信没有重叠（Overlap）。GPU 设备和网络设备是相互独立的，GPU 进行当前批次计算的同时，本可以让网络设备传输上一批次的数据，两者本可以同时工作。

针对这些问题，研究者提出了一些方法，从数据切分和重叠的角度优化流水线并行，以提高 GPU 利用率。这些方法在朴素流水线并行基础上进行改进，感兴趣的读者可以阅读以下原文，这里不再赘述。

* GPipe {cite}`huang2019GPipe`。
* PipeDream {cite}`narayanan2019PipeDream`。
* Megatron-LM {cite}`narayanan2021Efficient`。

## 流水线并行 + 数据并行

流水线并行与数据并行是两种互不干扰的方法，它们可以结合使用以提高计算效率。为了避免在数据传输过程中出现错乱，应使用 MPI 的 Communicator 来进行隔离和协调。正如我们在 {numref}`sec-mpi-hello-world` 中提到的，Communicator 在 MPI 中可以被理解为一个通信组，允许同一个 GPU 参与到多个不同的 Communicator 中。

如 {numref}`fig-pipeline-parallel-data-parallel` 所示，我们创建了两种类型的 Communicator：红色的用于流水线并行，而蓝色的用于数据并行。同一个 GPU 可以同时属于这两个 Communicator，这样它既能处理流水线并行中模型层之间的通信，也能参与数据并行中的梯度同步。

```{figure} ../img/ch-mpi-large-model/pipeline-parallel-data-parallel.svg
---
width: 600px
name: fig-pipeline-parallel-data-parallel
---
流水线并行结合数据并行
```

至此，我们介绍了两种最朴素的大模型并行训练方式：数据并行和流水线并行。工业级分布式训练库的实现比这些复杂，但背后的思想万变不离其宗。