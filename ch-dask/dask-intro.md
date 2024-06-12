# Dask 简介

Dask 是一个面向 Python 的并行计算框架，可以将计算任务扩展到多核和集群上。它提供了两类 API：高层的 DataFrame 和 Array 模拟了 pandas 和 NumPy 的 API，开箱即用；底层的基于计算图的 API 可以与很多 Python 包相结合。基于这两种 API，Dask 已经形成了一些生态，以应对越来越大的数据量和各种各样数据科学任务。

Dask 的核心思想是构建任务计算图（Task Graph），将一个大计算任务分解为任务（Task），每个任务调用那些单机的 Python 包（比如 pandas 和 NumPy）作为执行后端。

{numref}`fig-dask-overview` 展示了 Dask API 和 Task Graph 并最后调度到计算设备上的示意图。

```{figure} ../img/ch-dask/dask-overview.svg
---
width: 800px
name: fig-dask-overview
---
Dask 架构图
```

:::{note}
Dask 是一个面向大数据的并行计算框架，但 Dask 官方给用户的建议是：如果数据可以放进单机内存，建议优先使用传统的单机 Python 包。因为并不是所有的计算都很容易被并行化，有些任务甚至并行之后的性能反而下降。
:::

安装 Dask 也很简单，使用 `pip` 或者 `conda` 安装所需要的包：

```bash
pip instal dask[complete]
```

安装好后，我们就可以将 Dask 运行在单机的多个核心上。本书先从单机场景开始，多机场景只需修改一下调度器（Scheduler）即可。