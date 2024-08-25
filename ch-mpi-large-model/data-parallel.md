(sec-data-parallel)=
# 数据并行

数据并行是大模型并行方法中最常见的一种，并且相对于其他并行方法来说，数据并行在实现上更为简单直观。如 {numref}`fig-data-parallel-img` 所示，模型的副本被加载到不同的 GPU 设备上，而训练数据则被分割成多个份，每个份由不同的 GPU 独立进行训练。这种编程模式被称为单程序多数据（Single Program Multiple Data， SPMD）。

```{figure} ../img/ch-mpi-large-model/data-parallel.svg
---
width: 500px
name: fig-data-parallel-img
---
数据并行示意图
```

## 非并行训练

{numref}`sec-machine-learning-intro` 介绍了神经网络模型训练的过程。我们首先从非并行的场景开始讨论，在这一场景中，使用 MNIST 手写数字识别案例进行演示。如 {numref}`fig-data-parallel-single` 所示，该案例展示了一次前向传播和一次反向传播的过程。

```{figure} ../img/ch-mpi-large-model/data-parallel-single.svg
---
width: 600px
name: fig-data-parallel-single
---
在单个 GPU 上进行神经网络训练
```

## 数据并行

数据并行技术涉及将数据集分割成多份，并在不同的 GPU 上复制模型权重。如 {numref}`fig-data-parallel-distributed` 所示，假设有两块 GPU，每块 GPU 上都有一个模型权重的副本以及相应切分的输入数据子集。在每块 GPU 上，都会**独立**进行前向传播和反向传播的过程：前向传播负责计算每层的输出值，而反向传播则用于计算模型权重的梯度。这些计算在不同的 GPU 之间是相互独立的，互不干扰。

```{figure} ../img/ch-mpi-large-model/data-parallel-distributed.svg
---
width: 600px
name: fig-data-parallel-distributed
---
在两个 GPU 上进行神经网络训练
```

至少在前向传播和反向传播阶段，还没有通信的开销。但到了更新模型权重部分，需要进行必要的同步，因为每块 GPU 上得到的梯度不一样，可以用求平均的方式求得梯度。这里只演示 $\boldsymbol{W}$，$\boldsymbol{\frac{\partial L}{\partial W}}^{i}$ 为单块 GPU 上的梯度，$\boldsymbol{{\frac{\partial L}{\partial W}}^{sync}}$ 为同步之后的平均值。

$$
\boldsymbol{
    {\frac{\partial L}{\partial W}}^{sync} = \frac{1}{\# GPUs} \sum_{i=0}^{\# GPUs} {\frac{\partial L}{\partial W}}^{i}
}
$$

同步不同 GPU 上的梯度，可以使用 MPI 提供的 `AllReduce` 原语。MPI 的 `AllReduce` 将每块 GPU 上独立计算得到的梯度收集起来，进行平均计算，然后将计算得到的平均梯度广播回各块 GPU。

如 {numref}`fig-data-parallel-all-reduce` 所示，在梯度同步阶段，MPI 的 `AllReduce` 原语确保了各 GPU 上梯度的一致性。

```{figure} ../img/ch-mpi-large-model/data-parallel-all-reduce.svg
---
width: 600px
name: fig-data-parallel-all-reduce
---
在进行模型权重更新时，要使用 MPI 的 `AllReduce` 原语，将各 GPU 上的梯度进行同步
```