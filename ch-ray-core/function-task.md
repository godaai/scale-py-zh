```{.python .input  n=1}
%load_ext d2lbook.tab
tab.interact_select(['ray'])
```

分布式函数
--------

被 Ray 加速的函数又被称为 Task。Ray Task 是无状态的，无状态的意思是的执行只依赖函数的输入和输出，不依赖其他第三方的中间变量。

### 顺序执行与分布式执行

一个原生的 Python 函数如果使用 `for` 循环多次执行，将以顺序的方式，依次执行，如 :numref:`serial-timeline` 所示。

![顺序执行的时间轴示意图](../img/ch-ray-core/serial-timeline.png)
:width:`800px`
:label:`serial-timeline`

与原生 Python 函数顺序不同的是，Ray 可以将函数的执行分布式到集群中的多个计算节点上，如 :numref:`distributed-timeline` 所示。

![分布式执行的时间轴示意图](../img/ch-ray-core/distributed-timeline.png)
:width:`800px`
:label:`distributed-timeline`

接下来将以三个案例来演示如何将 Python 函数横向扩展到 Ray 集群上：

* 生成斐波那契数列
* 使用蒙特卡洛方法计算 $\pi$
* 并行化地图片处理

```{.python .input  n=2}
%%tab ray
import os
import time
import logging
import math
import random
from pathlib import Path
from typing import Tuple, List
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import tqdm
import ray
```

### 启动 Ray 集群

在正式使用 Ray 的分布式功能之前，首先要启动一个 Ray 集群。启动 Ray 集群的方式有很多种，我们可以使用 `ray.init()` 函数，先在自己的个人电脑上启动一个 Ray 集群，以便后续的演示。

```{.python .input  n=3}
%%tab ray
if ray.is_initialized:
    ray.shutdown()
ray.init(logging_level=logging.ERROR)
```

### 案例1：斐波那契数列

接下来，我们用斐波那契数列的案例来演示如何使用 Ray 对 Python 函数进行分布式的扩展。

斐波那契数列的第 $n$ 项 $F_n$ 可以由它前面的两个数 $F_{n-1}$ 和 $F_{n-2}$ 计算得到。用形式化的数学公式定义为：

$$
F_n = F_{n-1} + F_{n-2}
$$

其中，$F_0 = 0$，$F_1 = 1$。

下面我们使用原生的 Python 定义一个斐波那契函数。

```{.python .input  n=4}
%%tab ray
SEQUENCE_SIZE = 100000

def generate_fibonacci(sequence_size):
    fibonacci = []
    for i in range(0, sequence_size):
        if i < 2:
            fibonacci.append(i)
            continue
        fibonacci.append(fibonacci[i-1] + fibonacci[i-2])
    return len(fibonacci)
```

如果我们想让这个 Python 函数被 Ray 分布式执行，只需要在函数上增加一个 `@ray.remote` 装饰器。

```{.python .input  n=5}
# 在函数上增加一个 @ray.remote 装饰器
@ray.remote
def generate_fibonacci_distributed(sequence_size):
    return generate_fibonacci(sequence_size)
```

作为 Ray 的使用者，我们不需要关心 Task 在 Ray 集群中是如何被分布式执行的，也不需要了解这个 Task 被调度到哪些计算节点。所有这些分布式执行的细节都被 Ray 所隐藏，或者说 Ray 帮我们做了底层的分布式与调度这些工作。

我们比较一下顺序执行与分布式执行的效率与耗时。`os.cpu_count()` 可以得到当前个人电脑上的 CPU 核心数。顺序执行的代码使用 `for` 循环，多次调用生成斐波那契数列的函数。

```{.python .input  n=6}
# 顺序执行
def run_local(sequence_size):
    results = [generate_fibonacci(sequence_size) for _ in range(os.cpu_count())]
    return results
```

```{.python .input  n=7}
%%time
run_local(SEQUENCE_SIZE)
```

使用 Ray 进行分布式扩展，函数可并行地在多个 CPU 核心上执行。

```{.python .input  n=8}
# 使用 Ray 进行分布式扩展
def run_remote(sequence_size):
    results = ray.get([generate_fibonacci_distributed.remote(sequence_size) for _ in range(os.cpu_count())])
    return results
```

```{.python .input  n=9}
%%time
run_remote(SEQUENCE_SIZE)
```

### 原生 Python 函数与 Ray 的区别

需要注意的是，使用 Ray 与原生 Python 函数稍有区别，主要体现在：

* 函数调用方式

原生 Python 函数，使用 `func_name()` 调用。在使用 Ray 是，函数定义需要增加 `@ray.remote` 装饰器，调用时需要使用 `func_name.remote()` 的形式。

* 返回值

调用一个原生 Python 函数 `func_name()`，即可得到函数的返回值。在使用 Ray 时，`func_name.remote()` 返回值是 `ray.ObjectRef` 类型的对象，`ray.ObjectRef` 并不是一个具体的值，而是一个 Future（尚未完成但未来会完成的计算），需要使用 `ray.get()` 函数获取该调用的实际返回值。

* 执行方式

原生 Python 函数 `func_name()` 的调用是同步执行的，或者说等待结果返回才进行后续计算，又或者说这个调用是阻塞的。一个 Ray 函数`func_name.remote()` 是异步执行的，或者说调用者不需要等待这个函数的计算真正执行完， Ray 就立即返回了一个 `ray.ObjectRef`，函数的计算是在后台某个计算节点上执行的。`ray.get(ObjectRef)` 会等待后台计算结果执行完，将结果返回给调用者。`ray.get(ObjectRef)` 是一个一个阻塞调用。

### 案例2：使用蒙特卡洛方法计算 $\pi$
