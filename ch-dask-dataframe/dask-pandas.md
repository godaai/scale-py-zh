# Dask DataFrame 与 pandas

pandas 已经成为 DataFrame 的标准，但无法利用多核和集群，Dask DataFrame 试图解决 pandas 并行计算的问题。Dask DataFrame 尽量提供与 pandas 一致的 API，但使用起来，Dask DataFrame 仍有很多不同。本章假设用户已经了解并熟悉 pandas，并重点讨论 Dask DataFrame 与 pandas 的区别。