# Ray Data
:label:`ray-data`

```{.python .input}
# Hide code
# Hide outputs
import os
from pathlib import Path
import urllib.request
import shutil

import pandas as pd
import ray

if ray.is_initialized:
    ray.shutdown()

ray.init()
```

Ray Data 是基于 Ray Core 的一个数据处理框架，主要解决机器学习模型训练或推理前的数据准备与处理问题，即数据的最后一公里问题（Last-mile Preprocessing）。

Ray Data 提供了常见的大数据处理的原语，例如：

* 对数据的转换（Transformation）操作，比如 [map_batches()](https://docs.ray.io/en/latest/data/api/doc/ray.data.Dataset.map_batches.html#ray.data.Dataset.map_batches)。
* 分组聚合操作，比如 [groupby()](https://docs.ray.io/en/latest/data/api/doc/ray.data.Dataset.groupby.html#ray.data.Dataset.groupby)。
* 涉及数据在计算节点间的交换，比如 [random_shuffle](https://docs.ray.io/en/latest/data/api/doc/ray.data.Dataset.random_shuffle.html#ray.data.Dataset.random_shuffle) 和 [repartition](https://docs.ray.io/en/latest/data/api/doc/ray.data.Dataset.repartition.html#ray.data.Dataset.repartition) 等。

### 主要工作流

Ray Data 面向机器学习，其设计理念也与机器学习的流程高度一致。它主要包括了：

* 数据读取与存储
* 数据转换
* 机器学习特征预处理、数据集与机器学习模型的紧密结合

### Dataset

Ray Data 主要基于 `ray.data.Dataset` 对象。`Dataset` 是一个分布式的数据对象，`Dataset` 底层的基本单元是 `Block`，`Dataset` 是多个 `Block` 组成的分布式的 `ObjectRef[Block]`。 `Block` 是一个基于 Apache Arrow 格式的数据结构。 

我们可以使用 `from_*()` API 从其他系统或格式导入成 `Dataset`，比如 `from_pandas()` 、`from_spark()`。或者使用 `read_*()` API 从持久化的文件系统重读取，比如 `read_parquet()`、`read_json()` 等。

```{.python .input}
folder_path = os.path.join(os.getcwd(), "../data/nyc-taxi")
download_url = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-06.parquet"
file_name = download_url.split("/")[-1]
parquet_file_path = os.path.join(folder_path, file_name)
if not os.path.exists(folder_path):
    # 创建文件夹
    os.makedirs(folder_path)
    print(f"文件夹 {folder_path} 不存在，已创建。")

    # 下载并保存 Parquet 文件
    with urllib.request.urlopen(download_url) as response, open(parquet_file_path, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
    print("数据已下载并保存为 Parquet 文件。")
else:
    print(f"文件夹 {folder_path} 已存在，无需操作。")
```

使用 `ray.data` 读取文件：

```{.python .input}
dataset = ray.data.read_parquet(parquet_file_path)
```

查看这份数据集的表模式（Schema）：

```{.python .input}
dataset.schema()
```

查看数据集的样本数目：

```{.python .input}
dataset.count()
```

查看数据集中的前几个数据：

```{.python .input}
dataset.take(1)
```

### Transformation

对于 `Dataset` 中的每条数据，可以使用一些用户自定义的转换或者 Ray 提供的转换对数据进行预处理。比如，使用 [map_batches()](https://docs.ray.io/en/latest/data/api/doc/ray.data.Dataset.map_batches.html#ray.data.Dataset.map_batches) 对数据进行预处理。

Ray 也提供了 `map()` 和 `flat_map()` 这两个 API，与其他大数据框架类似，比如 Spark 或者 Flink。即对数据集中的每一行（row）数据一一进行转换。这里不再赘述。`map_batch()` 对数据集中的一个批次进行转化操作，一般是一个批次的输入对应一个批次的输出。

![map() v.s. map_batches()](../img/ch-ray-air/map-map-batches.svg)
:width:`800px`
:label:`map-map-batches`

`map_batches()` 解决的是从单机处理直接迁移到集群处理的问题。其设计思想主要为了方便将之前编写好的、单机的程序，无缝地迁移到 Ray 上。所以，我们可以简单理解为，用户先编写一个单机的程序，然后使用 `map_batches()` 迁移到集群上。每个批次的数据格式为 `Dict[str, np.ndarray]`、`pd.DataFrame` 或 `pyarrow.Table` 表示，分别对应使用 NumPy 、pandas 和 Arrow 时，进行单机处理的业务逻辑。`map_batches()` 最重要的参数是一个自定义的函数 `fn`。比如，我们对 `dataset` 中过滤某个字段的值，可以看到，经过过滤之后，数据的条数大大减少。

```{.python .input}
lambda_filterd_dataset = dataset.map_batches(lambda df: df[df["passenger_count"] == 0],  batch_format="pandas")
lambda_filterd_dataset.count()
```

在实现这个自定义函数时，我们使用了一个 Python 的 lambda 表达式，即一个匿名的 Python 函数。当然，我们也可以传入一个标准的 Python 函数。比如：

```{.python .input}
def filter_pa_cnt(df: pd.DataFrame) -> pd.DataFrame:
    df = df[df["passenger_count"] == 0]
    return df

filterd_dataset = dataset.map_batches(filter_pa_cnt, batch_format="pandas")
filterd_dataset.count()
```

默认情况下，`map_batches()` 使用的是 Ray 的 Remote Function。当然也可以使用 Actor 模型，感兴趣的读者可以参考文档，这里暂不赘述。

### groupby

数据处理中另外一个经常使用的原语是分组聚合，Ray Data 提供了： [groupby()](https://docs.ray.io/en/latest/data/api/doc/ray.data.Dataset.groupby.html#ray.data.Dataset.groupby)。Ray Data 先调用 `groupby()`，对数据按照某些字段进行分组，再调用 `map_groups()` 对分组之后的数据进行聚合。

`groupby()` 的参数是需要进行分组的字段，`map_groups()` 的参数是一个 Python 函数，即对同一个组的数据进行操作。Ray Data 预置了一些聚合函数，比如常见的求和 `sum()`，最大值 `max()`，平均值 `mean()` 等。

```{.python .input}
ds = ray.data.from_items([ 
    {"group": 1, "value": 1},
    {"group": 1, "value": 2},
    {"group": 2, "value": 3},
    {"group": 2, "value": 4}])
mean_ds = ds.groupby("group").mean("value")
mean_ds.show()
```

### materialize

Ray Data 的计算是延迟执行的，也就是说，如果不 `show()` 或者 `take()` 来查看数据集的内容，计算是不会被执行的，如果想立即执行，需要调用 `materialize()`。`materialize()` 借鉴了数据库中的物化的概念，它会触发对应的计算，将结果收集到 Ray 的分布式对象存储中。

### 数据预处理与模型训练

将数据集切分为训练集和测试集：

```{.python .input}
train_dataset, valid_dataset = dataset.train_test_split(test_size=0.3)
```

```
from ray.data.preprocessors import MinMaxScaler

preprocessor = MinMaxScaler(columns=["trip_distance", "trip_duration"])

from ray.data.preprocessors import PowerTransformer

# create a copy
sample_data = train_dataset

# create new preprocessor
sample_preprocessor = PowerTransformer(columns=["trip_distance"], power=0.5)

# apply the transformation
transformed_data = sample_preprocessor.fit_transform(sample_data)
```
