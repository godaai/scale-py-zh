(sec-data-parallel)=
# 数据并行

数据并行是一种最常见的大模型并行方法，相对其他并行，数据并行最简单。如 {numref}`fig-data-parallel-img` 所示，模型被拷贝到不同的 GPU 设备上，训练数据被切分为多份，每份分给不同的 GPU 进行训练。这种编程范式又被称为单程序多数据（Single Program Multiple Data，SPMD）。

```{figure} ../img/ch-mpi-large-model/data-parallel.svg
---
width: 500px
name: fig-data-parallel-img
---
数据并行示意图
```

## 非并行训练

{numref}`sec-machine-learning-intro` 介绍了神经网络模型训练的过程。我们先从非并行的场景开始，这里使用 MNIST 手写数字识别案例来演示，如 {numref}`fig-data-parallel-single` 所示，它包含了一次前向传播和一次反向传播。

```{figure} ../img/ch-mpi-large-model/data-parallel-single.svg
---
width: 600px
name: fig-data-parallel-single
---
在单个 GPU 上进行神经网络训练
```

## 数据并行

数据并行将数据集切分成多份，模型权重在不同 GPU 上拷贝一份。如 {numref}`fig-data-parallel-distributed` 所示，有两块 GPU，在每块 GPU 上，有拷贝的模型权重和被切分的输入数据集；每块 GPU 上**独立**进行前向传播和反向传播，即前向传播计算每层的输出值，反向传播计算模型权重的梯度，两块 GPU 上的计算互不影响。


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

同步不同 GPU 上的梯度，可以使用 MPI 提供的 `AllReduce` 原语。MPI 的 `AllReduce` 将每块 GPU 上分别计算得到的梯度收集起来，计算平均后，再将更新后的梯度重新分发给各块 GPU。

如 {numref}`fig-data-parallel-all-reduce` 所示，梯度同步阶段，MPI 的 `AllReduce` 原语将各 GPU 上的梯度进行同步。

```{figure} ../img/ch-mpi-large-model/data-parallel-all-reduce.svg
---
width: 600px
name: fig-data-parallel-all-reduce
---
在进行模型权重更新时，要使用 MPI 的 `AllReduce` 原语，将各 GPU 上的梯度进行同步
```