# 分组汇总
:label:`dataframe-groupby`

实际的数据分析中，经常需要对某一类数据进行统计分析。比如，假如我们拥有全国所有人的身高和体重数据，我们想按照省份分组，统计每个省的平均身高和平均体重，这时候就需要使用分组操作。pandas 提供了 `groupby` 函数进行类似的分组汇总操作。:numref:`groupby-img` 计算平均身高的分组汇总流程，主要包括两部分：分组与汇总。其中分组阶段将同一类的内容归结到相同的组中；汇总阶段将所关心的数据进行计算，比如求和、求平均等。

按哪些字段进行分组，这些字段又被成为 ** 分组变量 **。对其他字段进行汇总，其他汇总字段被成为 ** 汇总变量 **。对汇总变量进行计算，被称为 ** 汇总统计量 **。

![分组与汇总](../img/ch-pandas/groupby.svg)
:width:`800px`
:label:`groupby-img`

```{.python .input}
# Hide outputs
# Hide code
import urllib.request
import zipfile
import os

import pandas as pd

folder_path = os.path.join(os.getcwd(), "./data/pwt")
download_url = "https://www.rug.nl/ggdc/docs/pwt70_06032011version.zip"
file_name = download_url.split("/")[-1]
if not os.path.exists(folder_path):
    # 创建文件夹
    os.makedirs(folder_path)
    print(f"文件夹不存在，已创建。")

    zip_file_path = os.path.join(folder_path, file_name)

    urllib.request.urlretrieve(download_url, zip_file_path)
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(folder_path)
    print("数据已下载并解压缩。")
else:
    print(f"文件夹已存在，无需操作。")

df = pd.read_csv(os.path.join(folder_path, "pwt70_w_country_names.csv"))
df = df.fillna(0)
```

### 分组变量

在进行分组汇总时，分组变量可以有一个或多个。

例如，按照 `country` 和 `year` 分组，并对 `tcgdp` 汇总求平均值，此时在 `groupby` 后接多个分组变量，以列表形式写出。或者是 `.groupby(by=['country','year'])`。`.groupby` 之后要接上所需要汇总的字段，这个例子是 `tcgdp`。最后要接上所需要进行的汇总计算，比如 `.mean()`。计算结果中产生了多个索引，本例中是 `country` 和 `year`，指代相应组的情况。

```{.python .input}
df.groupby(['country','year'])[['tcgdp']].mean()
```

### 汇总变量

在进行分组汇总时，汇总变量也可以有一个或多个。

例如按照 `year` 汇总 `tcgdp` 和 `POP`，在 `.groupby` 后直接使用 `[]` 筛选相应列，再接汇总统计量。

```{.python .input}
df.groupby(['year'])['tcgdp','POP'].mean()
```

### 汇总统计量

`groupby` 后可接的汇总统计量有：

- mean - 均值

- max - 最大值

- min - 最小值

- median - 中位数

- std - 标准差

- mad - 平均绝对偏差

- count - 计数

- skew - 偏度

- quantile - 指定分位数

这些统计量可以直接接 groupby 对象使用，此外，`agg` 方法提供了一次汇总多个统计量的方法。

例如，汇总各个国家 `country` 人口 `POP` 的均值、最大值、最小值。

```{.python .input}
df.groupby(['country'])['POP'].agg(['mean','min','max'])
```

### 多重索引

在进行分组汇总操作时，产生的结果并不是常见的二维表数据框，而是具有多重索引的数据框。 pandas 开发者设计这种类型的数据框是借鉴了 Excel 数据透视表的功能。

例如，按照 `country` 和 `year` 顺序对 `tcgdp` 和 `POP` 进行分组汇总，汇总统计量为最小值和最大值。

```{.python .input}
df.groupby(['country','year'])['tcgdp','POP'].agg(['min','max'])
```

此时数据框中有两个行索引（`country` 和 `year`）和两个列索引（`tcgdp` + `POP` 和 `min` + `max`）。需要筛选列时，第一个 `[]` 筛选第一重列索引（从 `tcgdp` 和 `POP` 中选择一个列），第二个 `[]` 筛选第二重列索引（从 `min` 和 `max` 中选择一个列）。

例如，查询各个国家 `country` 各年 `year` 人口 `POP` 的最小值。

```{.python .input}
df_query = df.groupby(['country','year'])['tcgdp','POP'].agg(['min','max'])
df_query['POP']['min']
```

