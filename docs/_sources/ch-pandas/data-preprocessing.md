# 数据处理
:label:`data-preprocessing`

数据处理工作包括处理重复值、缺失值和异常值，生成新的列或者行等。

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

### 处理重复值

检测数据集的记录是否存在重复，可以使用 `.duplicated` 函数进行验证，但是该函数返回的是数据集每一行的检测结果，即 n 行数据会返回 n 个布尔值。为了能够得到最直接的结果，可以使用 `any` 函数。该函数表示的是在多个条件判断中，只要有一个条件为 True，则 `any` 返回的结果为 True。

```{.python .input}
any(df.duplicated())
```

如果有重复项，可以通过 `.drop_duplicated()` 删除。该函数有 inplace 参数，设置为 True 表示直接在原始数据集上做操作：`df.drop_duplicated(inplace = True)`。

### 处理缺失值

缺失值是指数据集中的某些观测存在遗漏。数据缺失可能有两方面原因：一方面是人为原因，如记录过程中的遗漏、个人隐私而不愿意透露等；另一方面是机器或设备的故障所导致。

可以使用 `.isna()` 或 `.isnull()` 函数查看缺失值。这两个函数返回 `DataFrame` 每个元素是否有缺失值，如果有缺失值，比如 N/A 或`null`，则返回 True；否则返回 False。

例如：通过 `.sum()` 查看每一列的空缺值计数。

```{.python .input}
df.isnull().sum()
```

一般而言，遇到缺失值时，可以采用三种方法处理，分别是删除法、替换法或插补法。

删除法是指当缺失的观测比例非常低（如 5% 以内），直接删除存在缺失的观测，或者当某些变量的缺失比例非常高时（如 85% 以上），直接删除这些缺失的变量。
  
可以使用 `.dropna()` 函数删除有缺失值的行或列。具体形式：`df.dropna(axis=0, how='any', inplace=False)`。

这个函数有参数 `axis`，`axis` 用来指定要删除的轴。`axis=0` 表示删除行（默认），axis=1 表示删除列。`how` 用来指定删除的条件。`how='any'` 表示删除包含任何缺失值的行（默认），`how='all'` 表示只删除所有值都是缺失值的行。`inplace` 用于指定是否在原始 `DataFrame` 上进行修改，默认为 False，表示不修改原始 `DataFrame`，而是返回一个新的 `DataFrame`。

例如，删除包含任何缺失值的行。
    
```{.python .input}
ddf = df.dropna()
```

`.fillna()` 函数填补数据框中的缺失值。例如，将 `DataFrame` 中的缺失值用 0 填充。

```{.python .input}
fill_zero_df = df.fillna(0)
```

对于时间类型的数据集，可以用 `.fillna()` 的 `method` 参数，可以接受 `ffill` 和 `bfill` 两种值，分别代表前向填充和后向填充，使得数据前后具有连贯性，而一般的独立性样本并不适用该函数。（前向填充是指用缺失值的前一个值替换，而后向填充是指用缺失值的后一个值替换。）

### Apply 函数

`.apply()` 函数也是一个 pandas 中常用的函数。它可以对每行 / 列（也可以对基于切片选择特定的列或行）应用一个函数并返回一个 `Series`。该函数可以是一些内置函数，如 max 函数、lambda 函数或自定义函数。

- max 函数

例如，返回 `year`, `POP`, `XRAT`, `tcgdp`, `cc`, `cg` 列的最大值（当该列有空值时，无法计算最大值，则返回空值）。
    
```{.python .input}
df[['year', 'POP', 'XRAT', 'tcgdp', 'cc', 'cg']].apply(max)
```

- lambda 函数，形式为 `lambda arguments: expression`

lambda 函数是一种没有函数名，但是可以被调用执行的函数。换句话说，lambda 函数不需要用 `def func_name()` 来定义函数名，而是直接定义函数体中的计算部分。关于函数体部分，`arguments` 是参数列表，可以指定一个或多个参数，就像定义普通函数一样；`expression` 是一个表达式，定义了 lambda 函数的计算逻辑，通常包括使用参数执行哪些计算，并返回计算结果。lambda 函数通常用于一次性的、简单的操作。

例如，对每一行返回数据本身，不做任何其他操作：

```{.python .input}
df.apply(lambda row: row, axis=1)
```

在这个例子中，`apply` 有个参数为 `axis`，`axis = 1` 设置函数对每一行操作；`axis = 0`` 设置函数对每一列操作；默认 axis = 0。

例：和 `.loc[]` 一起使用，进行更高级的数据切片。`.apply()` 返回对每一行做条件判断的一系列布尔值，以 `[]` 操作选择部分列。下面的选择条件为：如果 `country` 列属于特定国家，且 `POP > 40000`；如果 `country` 列不属于特定国家，且 `POP < 20000`
    
```{.python .input}
complexCondition = df.apply(
lambda row: row.POP > 40000 if row.country in ['Argentina', 'India', 'South Africa'] else row.POP < 20000,
axis=1), ['country', 'year', 'POP', 'XRAT', 'tcgdp']
complexCondition
```

```{.python .input}
df.loc[complexCondition]
```

则返回符合条件的行和列。

### 更改 DataFrame 

更改 `DataFrame` 的部分值（行、列）在数据分析过程中十分重要。

- `.where()` 函数保留行，并用其他值替代其余行。

例：找出 POP 大于 20000 的行，保留这些行，其余部分用 `other` 替代，`other` 参数可以是任意值，比如 0 、"hello" 等。

```{.python .input}
df.where(df.POP > 20000, other=False)
```

- `.loc[]` 函数指定想修改的列，并赋值。

例：找出 cg 列的最大值，赋值为 1 。

```{.python .input}
df.loc[df.cg == max(df.cg), 'cg'] = 1
```

- `.apply()` 函数，根据自定义函数修改行和列。

例：将 POP 小于 10000 的修改为 1， 将 XRAT 缩小十倍。

```{.python .input}
def update_row(row):
  # modify POP
  row.POP = 1 if row.POP<= 10000 else row.POP

  # modify XRAT
  row.XRAT = row.XRAT / 10
  return row

df.apply(update_row, axis=1)
```

- `.applymap()` 函数，修改 `DataFrame` 中的所有单独元素。

例：将 DataFrame 中的数值型元素保留两位小数。

```{.python .input}
df.applymap(lambda x : round(x, 2) if type(x)!=str else x)
```

- `del` 函数删除指定列。

例：删除 `ppp` 列。

```{.python .input}
del df['ppp']
```

- `df['new_column'] = values` 增加新列。

例：增加一列 `GDP percap` 显示人均 GDP。
    
```{.python .input}
df['GDP percap'] = df['tcgdp'] / df['POP']
```

- `astype()` 更改变量数据类型

例：将 country 列改为字符串类型。

```{.python .input}
df.country = df.country.astype('str')
```

### 数据排序

在很多分析任务中，需要按照某个或某些指标对数据进行排序。pandas 在排序时，根据排序的对象不同可细分为 `sort_values` 和 `sort_index`, 与其字面意义相一致，分别代表了对值进行排序和对索引 index 进行排序。

- `.sort_values()` 函数，按照指定列排序。

形如 `.sort_values(by='column1', ascending = True/False)`，`ascending` 参数设置为 True 表示升序，False 为降序。例如按照 POP 列升序排列：
  
```{.python .input}
df = df.sort_values(by='POP', ascending = True)
df
```

也可以对多个列排序。例如按照 POP 列和 year 列降序排列。
  
```{.python .input}
df = df.sort_values(by=['POP','year'], ascending = False)
df
```

- `.sort_index()` 函数，按照现有的 index 索引排序，index 通常为打印 `DataFrame` 时，最左侧没有任何列名的那一列。

```{.python .input}
df.sort_index()
```
