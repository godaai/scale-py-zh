# Series 与 DataFrame
:label:`series-dataframe`

pandas 的核心数据结构有两个： Series 和 DataFrame。

```{.python .input}
# Hide outputs
# Hide code
import pandas as pd
```

### Series

在 pandas 中，`Series` 是一种一维的带标签的 **数组状** 数据结构。

我们首先以 4 个数创建一个 `Series`，并命名为 `my_series`。

```{.python .input}
s = pd.Series([1, 2, 3, 4], name = 'my_series')
```

`Series` 是一个数组状数据结构，数组最重要的结构是索引（index）。index 主要用于标记第几个位置存储什么数据。`pd.Series()` 中不指定 index 参数时，默认从 0 开始，逐一自增，形如： 0，1，...

- Series 支持计算操作。

```{.python .input}
s * 100
```

- Series 支持描述性统计。比如，获得所有统计信息。

```{.python .input}
s.describe()
```

计算平均值，中位数和标准差。

```{.python .input}
s.mean()
```

```{.python .input}
s.median()
```

```{.python .input}
s.std()
```

- Series 的索引很灵活。

```{.python .input}
s.index = ['number1','number2','number3','number4']
```

这时，`Series` 就像一个 Python 中的字典 `dict`，可以使用像 `dict` 一样的语法来访问 `Series` 中的元素，其中 `index` 相当于 `dict` 的键 `key`。例如，使用 `[]` 操作符访问 `number1` 对应的值。

```{.python .input}
s['number1']
```

又例如，使用 `in` 表达式判断某个索引是否在 Series 中。

```{.python .input}
'number1' in s
```

### DataFrame

`DataFrame` 可以简单理解为一个 Excel 表，有很多列和很多行。
`DataFrame` 的列（column）表示一个字段；`DataFrame` 的行（row）表示一条数据。`DataFrame` 常被用来分析像 Excel 这样的、有行和列的表格类数据。Excel 也正在兼容 `DataFrame`，使得用户在 Excel 中进行 pandas 数据处理与分析。

### 创建 DataFrame

创建一个 `DataFrame` 有很多方式，比如从列表、字典、文件中读取数据，并创建一个 `DataFrame`。

- 基于列表创建

```{.python .input}
names = ['Alice', 'Bob', 'Charlie']
ages = [25, 30, 22]
cities = ['New York', 'San Francisco', 'Los Angeles']
data = {'Name': names, 'Age': ages, 'City': cities}
df = pd.DataFrame(data)
```

- 基于字典创建

```{.python .input}
data = {'Column1': [1, 2], 'Column2': [3, 4]}
df = pd.DataFrame(data)
```

- 基于文件创建

对于不同类型的文件，使用不同的函数，比如 `read_csv` 读取 csv 类型的数据。`df = pd.read_csv('/path/to/csv')` 用来读取一个 csv 文件，`df =  pd.read_excel('/path/to/excel')` 用来读取一个 Excel 文件。

> 注：csv 文件一般由很多个 column 组成，使用 `pd.read_csv` 时，默认每个 column 之间的分隔符为逗号（`,`），`pd.read_table` 默认分隔符为换行符。这些函数还支持许多其他参数，可以使用 `help()` 函数查看。
> 例：help(pd.read_csv)

### 案例：PWT

[PWT](https://www.rug.nl/ggdc/productivity/pwt/) 是一个经济学数据库，用于比较国家和地区之间的宏观经济数据，该数据集包含了各种宏观经济指标，如国内生产总值（GDP）、人均收入、劳动力和资本等因素，以及价格水平、汇率等信息。我们先下载，并使用 pandas 简单探索该数据集。

```{.python .input}
import urllib.request
import zipfile
import os

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
```

### 查看数据

- 使用 `read_csv()` 读取数据。

```{.python .input}
import pandas as pd
df = pd.read_csv(os.path.join(folder_path, "pwt70_w_country_names.csv"))
```

- `head()` 函数可以指定查看前 n 行。

```{.python .input}
n = 5
df.head(n)
```

- `tail()` 函数指定查看后 n 行。

```{.python .input}
df.tail(n)
```

- `info()` 函数可以查看数据基本信息，包括字段类型和非空值计数。

```{.python .input}
df.info()
```

- `dtypes` 查看各变量数据类型。

```{.python .input}
df.dtypes
```

- `.columns` 查看数据框列名（变量名）。

```{.python .input}
df.columns
```

- `.index` 查看数据框行名。

```{.python .input}
df.index
```

- `.shape` 可以查看 `DataFrame` 的维度，返回一个 tuple（元组对象），显示数据框的行数和列数。因此，可以用索引分别查看数据框的行数和列数。

```{.python .input}
#查看数据框行数
print(df.shape[0])

#查看数据框列数
print(df.shape[1])
```



















