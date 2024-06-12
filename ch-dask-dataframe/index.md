# Dask DataFrame

pandas 已经成为 DataFrame 的标准，但无法利用多核和集群，Dask DataFrame 试图解决 pandas 并行计算的问题。Dask DataFrame 尽量提供与 pandas 一致的 API，但使用起来，Dask DataFrame 仍有很多不同。Dask DataFrame 将大数据切分成小的 Partition，每个 Partition 是一个 pandas DataFrame。Dask 会把 DataFrame 的元数据记录下来，存储在 `_meta` 中。多个 Partition 的信息存储在内置变量 `partitions` 里和 `divisions` 里。Dask 用 Task Graph 管理计算图。对于用户来说，其实不需要太深入理解 Dask DataFrame 具体如何实现的，只需要调用跟 pandas 类似的上层 API。本章假设用户已经了解并熟悉 pandas，并重点讨论 Dask DataFrame 与 pandas 的区别。

```{tableofcontents}
```