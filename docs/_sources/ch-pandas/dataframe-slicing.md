# 数据切片
:label:`dataframe-slicing`

实际中，我们常常不是分析整个数据，而是数据中的部分子集。如何根据特定的条件获得所需要的数据是本节的主要内容。

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
```

### 主要方法

对 `DataFrame` 选择行和列，主要有几种方式：

* 使用 `[]` 选择
* 使用 `.iloc` 或者 `.loc` 函数
* 使用 `.query` 函数

### 使用 [] 进行选择

选择第 2 行到第 5 行（不包括第 5 行）的数据：

```{.python .input}
df[2:5]
```

要选择列，我们可以传递一个列表，其中包含所需列的列名，为字符串形式。

```{.python .input}
df[['country', 'tcgdp']]
```

如果只选取一列，`df['country']` 等价于 `df.country`。

`[]` 还可以用来选择符合特定条件的数据。 例如，选取 POP 大于 20000 的行。判断语句 `df.POP> 20000` 会返回一系列布尔值，符合 POP 大于 20000 条件的会返回为 `True`。如果想要选择这些符合条件的数据，则需要：

```{.python .input}
df[df.POP>= 20000]
```

如果选择 cc 列和 cg 列的和大于 80 并且 POP 小于 20000 的行：

```{.python .input}
df[(df.cc + df.cg>= 80) & (df.POP <= 20000)]
```

### iloc 或者 loc

使用 `iloc` 函数进行选择，形式应为 `.iloc[rows, columns]`。

可以将 i 理解为 integer，即 i 是整数，表示行或者列位置（位置由被称为 index），`iloc` 即用整数来选择行或者选择列。i 从 0 开始，至 `length-1`。

例如：选择第 2 行到第 5 行（不包括第 5 行），第 0 列到第 4 列（不包括第 4 列）。

```{.python .input}
df.iloc[2:5, 0:4]
```

使用 `loc` 函数进行选择，与 `iloc` 的区别在于，`loc` 除了接受整数外，还可以接受标签（`a`、`b` 这样的列名）、表示整数位置的 index、`boolean` 。

选择第 2 行到第 5 行（不包括第 5 行），`country` 和 `tcgdp` 列：

```{.python .input}
df.loc[df.index[2:5], ['country', 'tcgdp']]
```

使用 `loc` 函数选择 POP 列最大值的行：

```{.python .input}
df.loc[df.POP == max(df.POP)]
```

还可以使用这种形式：`.loc[,]`，两个参数用逗号隔开，第一个参数接受条件，第二个参数接受我们想要返回的列名，得到的是符合条件的特定的列。

```{.python .input}
df.loc[(df.cc + df.cg>= 80) & (df.POP <= 20000), ['country', 'year', 'POP']]
```

由于 `iloc` 函数只接受整数，所以不允许使用这种条件进行筛选。

### query

`.query()` 函数的用法与 `[]` 有相似之处。值得注意的是，`.query()` 函数的性能更好，在处理大规模数据时更快。

```{.python .input}
df.query("POP>= 20000")
```

```{.python .input}
df.query("cc + cg>= 80 & POP <= 20000")
```

