(sec-dask-ml-preprocessing)=
# 数据预处理

{numref}`sec-data-science-lifecycle` 我们提到过，数据科学工作的重点是理解数据和处理数据，Dask 可以将很多单机的任务横向扩展到集群上，并且可以和 Python 社区数据可视化等库结合，完成探索性数据分析。

分布式数据预处理部分更多依赖 Dask DataFrame 和 Dask Array 的能力，这里不再赘述。

特征工程部分，Dask-ML 实现了很多 `sklearn.preprocessing` 的 API，比如 [`MinMaxScaler`](https://ml.dask.org/modules/generated/dask_ml.preprocessing.MinMaxScaler.html)。对 Dask 而言，稍有不同的是其独热编码，本书写作时，Dask 使用 [`DummyEncoder`](https://ml.dask.org/modules/generated/dask_ml.preprocessing.DummyEncoder.html) 对类别特征进行独热编码，`DummyEncoder` 是 scikit-learn `OneHotEncoder` 的 Dask 替代。我们将在 {numref}`sec-dask-ml-hyperparameter` 将展示一个类型特征的案例。