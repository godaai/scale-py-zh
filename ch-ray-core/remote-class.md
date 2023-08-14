# 分布式类
:label:`remote-class`

:numref:`remote-function` 展示了如何将一个无状态的函数扩展到 Ray 集群上进行分布式计算，但实际的场景中，我们经常需要进行有状态的计算。最简单的有状态计算包括维护一个计数器，每遇到某种条件，计数器加一。这类有状态的计算对于给定的输入，不一定得到确定的输出。单机场景我们可以使用 Python 的类（Class）来实现，计数器可作为类的成员变量。Ray 可以将 Python 类拓展到集群上，即远程类（Remote Class），又被称为行动者（Actor）。Actor 的名字来自 Actor 编程模型 :cite:`hewitt1973Universal`，这是一个典型的分布式计算编程模型，被广泛应用在大数据和人工智能领域，但 Actor 编程模型比较抽象，我们先从计数器的案例来入手。

### 案例1：分布式计数器

```{.python .input}
# Hide code
# Hide outputs
import logging
from typing import Dict, List, Tuple
import ray

if ray.is_initialized:
    ray.shutdown()
ray.init(logging_level=logging.ERROR)
```

Ray 的 Remote Class 也使用 `ray.remote()` 来装饰。

```{.python .input}
@ray.remote
class Counter:
    def __init__(self):
        self.value = 0

    def increment(self):
        self.value += 1
        return self.value

    def get_counter(self):
        return self.value
```

使用 Ray 创建一个类名为 `Counter` 的 Remote Class，需要在类名 `Counter` 后面加上 `remote()`。这样创建的类就是一个分布式的 Actor。

```{.python .input}
counter = Counter.remote()
```

接下来我们要使用 `Counter` 类的计数功能：`increment()` 函数，我们也要在函数后面添加 `remote()` ，即 `对象实例.函数名.remote()`。

```{.python .input}
obj_ref = counter.increment.remote()
print(ray.get(obj_ref))
```

我们可以用同一个类创建不同的 Actor 实例，不同 Actor 之间的成员函数调用可以被并行化执行，但同一个 Actor 的成员函数调用是顺序执行的。

```{.python .input}
# 创建 10 个 Actor 实例
counters = [Counter.remote() for _ in range(10)]

# 对每个 Actor 进行 increment 操作
# 这些操作可以分布式执行
results = ray.get([c.increment.remote() for c in counters])
print(results)
```

同一个 Actor 实例是互相共享状态的，所谓共享状态是指，Actor 可能被分布式地调度，无论调度到哪个计算节点，对 Actor 实例的任何操作都像对单机 Python 类和实例的操作一样，对象实例的成员变量的数据是可被访问、修改以及实时更新的。

```{.python .input}
# 对第一个 Actor 进行5次 increment 操作
# 这5次 increment 操作是顺序执行的，5次操作共享状态数据 value
results = ray.get([counters[0].increment.remote() for _ in range(5)])
print(results)
```

### Actor 编程模型

Actor 编程模型是一种分布式编程的范式，每门编程语言或框架有自己的实现。Actor 编程模型的基本要素是 Actor 实例，即每个 Actor 对象都是唯一的。我们可以把单个 Actor 实例理解成单个带地址信息的进程。每个 Actor 都拥有地址信息，我们就可以从别的 Actor 向这个 Actor 发送信息，就像我们通过手机号或电子邮件地址互相发送信息一样。一个 Actor 可以有一个地址，也可以有多个地址，多个 Actor 可以共享同一个地址，拥有多少个地址主要取决于我们想以怎样的方式收发数据。多个 Actor 共享同一个地址，就像公司里有一个群组邮箱，群组包含了多个人，有个对外的公共的地址，向这个群组发邮件，群组中的每个人都可以收到消息。

拥有地址和内存空间，Actor 可以做以下事情：

* 存储数据，比如状态数据
* 从别的 Actor 接收消息
* 向别的 Actor 接收消息
* 创建新的 Actor

Actor 存储的状态数据只能由 Actor 自己来管理，不能被其他 Actor 修改。这有点像面向对象编程语言中类的实例，如果想修改实例的数据，一般通过实例的成员函数。如果我们想修改 Actor 里面存储的状态数据，应该向 Actor 发送消息，Actor 接收到消息，并基于自己存储的数据，做出决策：决定修改状态数据，或者再向其他 Actor 发送消息。比如，刚才的计数器案例中，Actor 收到 `increment()` 的消息，并根据自己存储的状态，做自增操作。

为了保证 Actor 编程模型分布式环境下状态的一致性，对同一个 Actor 多次发送同样请求，多次请求是顺序执行的。就像计数器案例中，对同一个 Actor 进行5次 `increment()` 操作，这5次操作是顺序执行的。

Actor 编程模型是消息驱动的，给某个 Actor 发送消息，它就会对该消息进行响应，修改自身的状态或者继续给其他 Actor 发送消息。Actor 编程模型不需要显式地在多个进程之间同步数据，因此也没有锁的问题以及同步等待的时间。Actor 编程模型可被用于大量异步操作的场景。

### 案例2：排行榜

接下来我们基于 Actor 实现一个更加复杂的案例：成绩排行榜。这个排行榜的状态是一个键值对，名为 `self.board`，键是名字（`name`），是一个 `str` 类型，值是分数（`score`），是一个 `float` 类型。

```{.python .input}
@ray.remote
class Ranking:
    def __init__(self, minimal_score: float = 60.0):
        self.minimal = minimal_score
        self.board = dict()

    def add(self, name: str, score: float) -> Dict[str, float]:
        try:
            score = float(score)
            if score < self.minimal:
                return
            if name in self.board:
                self.board[name] = max(score, self.board[name])
            else:
                self.board[name] = score
            self.board = dict(sorted(self.board.items(), key=lambda item: item[1]))
            return self.board
        except Exception as e:
            print(f"The data type of score should be float but we receive {type(score)}.")
            return self.board

    def top(self, n: int = 1) -> List[Tuple[str, float]]:
        n = min(n, len(self.board))
        results = list(self.board.items())[:n]
        return results

    def pop(self) -> Dict[str, float]:
        if len(self.board) <= 0:
            raise Exception("The board is empty.")
        else:
            _, _ = self.board.popitem()
        return self.board
```

在这个排行榜的例子中，一共三个函数：

* `__init__()` ：构造器。
* `add()`：添加一条新记录，同时对输入进行解析，如果 `score` 不能转换成 `float` 会抛出异常；并对已有记录排序。
* `pop()`：删除最大值的那条记录，如果 `self.board` 为空，会抛出异常。

使用 `.remote()` 函数来创建这个 Remote Class 对应的 Actor 实例。

```{.python .input}
# 创建排行榜
ranking = Ranking.remote()
```

这里的 `ranking` 是一个 Actor 的引用（Actor Handle），有点像 `ObjectRef`，我们用 `ranking` 这个 Actor Handle 来管理这个 Actor。一旦 Actor Handle 被销毁，对应的 Actor 以及其状态也被销毁。

我们可以创建多个 Actor 实例，每个实例管理自己的状态。还可以用 `ActorClass.options` 给这些 Actor 实例设置一些选项，起名字，设置 CPU、GPU 计算资源等。

```{.python .input}
# 创建一个数学排行榜 math_ranking
# 它与刚创建的 ranking 相互独立
math_ranking = Ranking.remote(minimal_score=80)

# 创建一个化学排行榜 chem_ranking
# 并且有一个名字
chem_ranking = Ranking.options(name="Chemistry").remote()
```

有了名字之后，就可以通过 `ray.get_actor()` 来获取 Actor Handle，

```{.python .input}
# 获取名为 Chemistry 的 Actor Handle
cr = ray.get_actor("Chemistry")
```

向 `ranking` 排行榜内添加新记录，即调用 `add()` 函数。调用类成员函数，都要记得加上 `.remote()` ，否则会报错。

```{.python .input}
# 增加新记录
ranking.add.remote("Alice", 90)
ranking.add.remote("Bob", 60)

print(f"Current ranking: {ray.get(ranking.top.remote(3))}")
```

```{.python .input}
ray.get(ranking.add.remote("Mark", 'a88'))
```

在上面的案例中，有些调用会引发异常，比如插入一个字符串，Ray 通常会处理异常并打印出来，但是为了保险起见，你也可以在调用这些 Remote Class 的成员方法时手动做好 `try/except` 的异常捕获：

```
try:
    ray.get(ranking.pop.remote())
    ray.get(ranking.pop.remote())
    ray.get(ranking.pop.remote())
except Exception as e:
    print(e)
```

### 案例3：Actor Pool

实践上，经常创建一个 Actor 资源池（Actor Pool），Actor Pool 有点像 `multiprocessing.Pool`，Actor Pool 中有包含多个 Actor，每个 Actor 功能一样，而且可以分式地在多个计算节点上运行。

```{.python .input}
from ray.util import ActorPool

@ray.remote
class PoolActor:
    def add(self, operands):
        (a, b) = operands
        return a + b
    
    def double(self, operand):
        return operand * 2

# 将创建的 Actor 添加至 ActorPool 中
a1, a2, a3 = PoolActor.remote(), PoolActor.remote(), PoolActor.remote()
pool = ActorPool([a1, a2, a3])
```

如果我们想调用加入到 ActorPool 中的 Actor，可以使用 `map(fn, values)` 和 `submit(fn, value)` 方法。这两个方法非常相似，所接收的参数是一个函数 `fn` 和参数 `value` 或者参数列表 `values`。`map()` 的 `values` 是一个列表，让函数并行地分发给多个 Actor 去处理；`submit()` 的 `value` 是单个值，每次从 ActorPool 中选择一个 Actor 去执行。`fn` 是一个 Lambda 表达式，或者说是一个匿名函数。这个 Lambda 表达式有两个参数：`actor` 和 `value`，`actor` 就是我们定义的单个 Actor 的函数调用，`value` 是这个函数的参数。

函数的第一个参数是 ActorPool 中的 Actor，第二个参数是函数的参数。

```{.python .input}
pool.map(lambda a, v: a.double.remote(v), [3, 4, 5, 4])

pool.submit(lambda a, v: a.double.remote(v), 3)
pool.submit(lambda a, v: a.double.remote(v), 4)
```

`map()` 和 `submit()` 将计算任务提交到了 ActorPool 中，ActorPool 并不是直接返回结果，而是异步地分发给后台不同的 Actor 去执行。需要使用 `get_next()` 阻塞地返回结果。

```{.python .input}
try:
    print(pool.get_next())
    print(pool.get_next())
    print(pool.get_next())
except Exception as e:
    print(e)
```

当然，如果已经把所有结果都取回，仍然再去 `get_next()`，将会抛出异常。

在这里，`value` 只能是单个对象，不能是参数列表，如果想传入多个参数，可以把参数包裹成元组。比如 `add()` 方法对两个操作数做计算，我们把两个操作数包裹为一个元组，实现 `add()` 函数时使用 `(a, b) = operands` 解析这个元组。

```{.python .input}
pool.submit(lambda a, v: a.add.remote(v), (1, 10))
print(pool.get_next())
```

```{.python .input}
# Hide code
ray.shutdown()
```
