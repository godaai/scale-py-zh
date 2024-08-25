(sec-dask-ml-preprocessing)=
# 数据预处理

在 {numref}`sec-data-science-lifecycle` 中提到，数据科学工作的核心在于理解数据和处理数据。Dask 能够将许多单机任务扩展到集群上执行，并能与 Python 社区中的数据可视化等库结合，以完成探索性数据分析。

在分布式数据预处理方面，更多地依赖于 Dask DataFrame 和 Dask Array 的功能，这一点在此不再赘述。

在特征工程部分，Dask-ML 实现了很多 `sklearn.preprocessing` 的 API，比如 [`MinMaxScaler`](https://ml.dask.org/modules/generated/dask_ml.preprocessing.MinMaxScaler.html)。对 Dask 来说，一个稍有不同的地方是其独热编码的实现。截至本书写作时，Dask 使用 [`DummyEncoder`](https://ml.dask.org/modules/generated/dask_ml.preprocessing.DummyEncoder.html) 对类别特征进行独热编码，`DummyEncoder` 是 scikit-learn `OneHotEncoder` 的 Dask 替代。我们将在 {numref}`sec-dask-ml-hyperparameter` 展示一个关于类型特征的案例。