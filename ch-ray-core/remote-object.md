# 分布式对象存储
:label:`remote-object`

Ray 分布式计算中涉及共享数据可被放在分布式对象存储（Distributed Ojbect Store）中，被放置在分布式对象存储中的数据被称为远程对象（Remote Object）中。我们可以使用 `ray.get()` 和 `ray.put()` 读写这些 Remote Object。与内存中的 Python 对象实例不同，Remote Object 是不可原地直接更改的（Immutable）。

### ray.put() 与 ray.get()

```{.python .input}
# Hide code
# Hide outputs
import logging
import numpy as np
import pandas as pd
from typing import Tuple
import random
import torch
import ray

if ray.is_initialized:
    ray.shutdown()
ray.init(logging_level=logging.ERROR)
```

如 :numref:`put-get-object-store` 所示，操作 Remote Object 主要有 `ray.put()` 和 `ray.get()` 两个 API：`ray.put()` 与 `ray.get()` 。

* `ray.put()` 把某个计算节点中的对象数据进行序列化，并将其写入到 Ray 集群的分布式对象存储中，返回一个 `RefObjectID`，`RefObjectID` 是指向这个 Remote Object 的指针。我们可以通过引用这个 `RefObjectID`，在 Remote Function 或 Remote Class 中分布式地使用这个数据对象。

* `ray.get()` 使用 `RefObjectID` 从把数据从分布式对象存储中拉取回来，并进行反序列化。

![对象存储分布在多个节点，通过 ray.put() 向集群写数据，通过 ray.get() 从集群读数据](../img/ch-ray-core/put-get-object-store.png)
:width:`800px`
:label:`put-get-object-store`

```{.python .input}
def create_rand_tensor(size: Tuple[int, int, int]) -> torch.tensor:
    return torch.randn(size=(size), dtype=torch.float)

torch.manual_seed(42)
# 创建 16个 个机张量，每个张量大小为 (X, 8, 8)
tensor_obj_ref_list = [ray.put(create_rand_tensor((i, 8, 8))) for i in range(1, 16)]
tensor_obj_ref_list[0], len(tensor_obj_ref_list)
```

使用 `ray.get()` 从分布式对象存储中拉取数据。

```{.python .input}
val = ray.get(tensor_obj_ref_list[0])
val.size(), val
```

或者把存放 `ObjectRefIDs` 列表的所有对象都拉取过来：

```{.python .input}
results = ray.get(tensor_obj_ref_list)
results[0].size(), results[0]
```

### 对数据进行转换

Remote Object 的数据是不可原地更改的，比如下面的操作在单机的内存上可以，但是在 Remote Object 上，不可以直接在原地对 Remote Object 做更改。

```{.python .input}
a = torch.rand(size=(1, 8, 8))
a[0] = torch.ones(8, 8)
a
```

如果我们想使用新数据，应该使用 Remote Function 或者 Remote Class 对 Remote Object 进行转换操作，生成新的 Remote Object。

```{.python .input}
@ray.remote
def transform_tensor(tensor: torch.tensor) -> torch.tensor:
    return torch.transpose(tensor, 0, 1)

transformed_object_list = [transform_tensor.remote(t_obj_ref) for t_obj_ref in tensor_obj_ref_list]
transformed_object_list[0].size()
```

### 传递参数

Remote Object 可以通过 `RefObjectID` 在 Task、Actor 之间传递。

#### 直接传递

直接在 Task 或者 Actor 的函数调用时将 `RefObjectID` 作为参数传递进去。在下面这个例子中，`x_obj_ref` 是一个 `RefObjectID` ，`echo()` 这个 Remote Function 将自动从 `x_obj_ref` 获取 `x` 的值。这个自动获取值的过程被称为自动反引用（De-referenced）。

```{.python .input}
@ray.remote
def echo(x):
    print(f"current value of argument x: {x}")
    return x

x = list(range(5))
x_obj_ref = ray.put(x)
x_obj_ref
```

```{.python .input}
ray.get(echo.remote(x_obj_ref))
```

```{.python .input}
ray.get(echo.remote(x))
```

#### 复杂数据结构

如果 `RefObjectID` 被包裹在一个复杂的数据结构中，Ray 并不会自动获取 `RefObjectID` 对应的值，即 De-referenced 并不是自动的。复杂数据结构包括：

* `RefObjectID` 被包裹在一个 `dict` 中，比如：`.remote({"obj": x_obj_ref})`
* `RefObjectID` 被包裹在一个 `list` 中，比如：`.remote([x_obj_ref])`

```{.python .input}
echo.remote({"obj": x_obj_ref})
```

```{.python .input}
echo.remote([x_obj_ref])
```

### 底层实现

Ray 集群的每个计算节点都有一个基于共享内存的对象存储， Remote Object 的数据会存储在集群某个或者某些计算节点的对象存储中，所有计算节点的共享内存共同组成了分布式对象存储。

当某个 Remote Object 的数据量较小时（<= 100 KB），它会被存储在计算节点进程内存中；当数据量较大时，它会被存储在分布式的共享内存中；当集群的共享内存的空间不够时，数据会被外溢（Spill）到持久化的存储上，比如硬盘或者S3。

```{.python .input}
# Hide code
ray.shutdown()
```
