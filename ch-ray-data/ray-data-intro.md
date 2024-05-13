(sec-ray-data-intro)=
# Ray Data 简介

Ray Data 是基于 Ray Core 的数据处理框架，主要解决机器学习模型训练或推理相关的数据准备与处理问题，即数据的最后一公里问题（Last-mile Preprocessing）。与 Dask DataFrame、Modin、Xorbits 相比，Ray Data 更通用，既可以处理二维表，也可以处理图片、视频；Ray Data 的通用也意味着它在很多方面还不够专业，比如 `groupby` 等操作相对比较粗糙。除了 Ray Data 外，本章还会介绍 Modin。

Ray Data 对数据提供了一个抽象的类，[`ray.data.Dataset`](https://docs.ray.io/en/latest/data/api/doc/ray.data.Dataset.html)，在 `Dataset` 上提供了常见的大数据处理的原语，覆盖了数据处理的大部分阶段，例如：

* 数据的读取，比如读取 Parquet 文件等。
* 对数据的转换（Transformation）操作，比如 [`map_batches()`](https://docs.ray.io/en/latest/data/api/doc/ray.data.Dataset.map_batches.html)。
* 分组聚合操作，比如 [`groupby()`](https://docs.ray.io/en/latest/data/api/doc/ray.data.Dataset.groupby.html)
* 涉及数据在计算节点间的交换，比如 [`random_shuffle()`](https://docs.ray.io/en/latest/data/api/doc/ray.data.Dataset.random_shuffle.html) 和 [`repartition()`](https://docs.ray.io/en/latest/data/api/doc/ray.data.Dataset.repartition.html) 等。

## 关键概念

Ray Data 面向机器学习，其设计理念也与机器学习的流程高度一致。它主要包括了：

* 数据读取与存储
* 数据转换
* 机器学习特征预处理
* 数据集与机器学习模型的紧密结合

## Dataset

Ray Data 主要基于 `ray.data.Dataset` 对象。`Dataset` 是一个分布式的数据对象，`Dataset` 底层的基本单元是 `Block`。`Dataset` 是多个 `Block` 组成的分布式的 `ObjectRef[Block]`。 `Block` 是一个基于 Apache Arrow 格式的数据结构。 

{numref}`fig-ray-dataset-arch` 是一个示意图，这个数据由 3 个 `Block` 组成，每个 `Block` 有 1,000 行数据。

```{figure} ../img/ch-ray-data/dataset-arch.svg
---
width: 600px
name: fig-ray-dataset-arch
---
Ray Dataset 底层架构示意图
```

我们可以使用 `from_*()` API 从其他系统或格式导入成 `Dataset`，比如 [`from_pandas()`](https://docs.ray.io/en/latest/data/api/doc/ray.data.from_pandas.html) 、[`from_spark()`](https://docs.ray.io/en/latest/data/api/doc/ray.data.from_spark.html)。或者使用 `read_*()` API 从持久化的文件系统重读取，比如 [`read_parquet()`](https://docs.ray.io/en/latest/data/api/doc/ray.data.read_parquet.html)、[`read_json()`](https://docs.ray.io/en/latest/data/api/doc/ray.data.read_json.html) 等。

## 数据操作与底层实现

### 数据读写

如 {numref}`fig-ray-dataset-read` 所示，Ray Data 使用 Ray Task 并行地读写数据，Ray Task 的思想很直观，每个 Task 读取一小部分数据，得到多个 `Block`，读取时可以设置 `parallelism`。

```{figure} ../img/ch-ray-data/dataset-read.svg
---
width: 600px
name: fig-ray-dataset-read
---
数据读取原理示意图
```

### 数据转换

如 {numref}`fig-ray-dataset-map` 所示，数据转换操作底层使用 Ray Task 或 Ray Actor 对各个 `Block` 的数据进行操作。对于无状态的转换操作，底层实现主要使用 Ray Task；对于有状态的转换操作，底层实现主要使用 Ray Actor。

```{figure} ../img/ch-ray-data/dataset-map.svg
---
width: 600px
name: fig-ray-dataset-map
---
数据转换原理示意图
```

接下来我们详细介绍几类数据操作及其原理。