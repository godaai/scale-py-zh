(sec-ray-computing-resource)=
# 计算资源与资源组

## 计算资源

Ray 可以管理计算资源，包括 CPU、内存和 GPU 等各类加速器。这里的计算资源是逻辑上的，逻辑资源与物理上的计算资源相对应。Ray 集群的各个节点启动时会探测物理计算资源，并根据一定规则映射为逻辑上的计算资源。Ray 集群的各个节点可以是虚拟机、容器或者裸金属服务器。

* CPU：每个节点中的物理 CPU 个数（`num_cpus`）
* GPU：每个节点中的物理 GPU 个数（`num_gpus`）
* 内存：每个节点可用内存的 70%（`memory`）

以上为默认的规则。也可以在启动 Ray 集群时，手动指定这些资源。比如某台物理节点上有 64 个 CPU 核心，8 个 GPU，启动 Ray 工作节点时只注册一部分计算资源。

```
ray start --num-cpus=32 --num-gpus=4
```

## 资源需求

默认情况下，Ray Task会使用1个逻辑CPU，这个CPU既用于任务调度，也用于执行计算任务；而Ray Actor则使用1个逻辑CPU进行任务调度，0 个 CPU 用来运行计算任务。

Task 或 Actor 在执行时，Ray 会将其调度到能够满足其资源需求的节点上。在默认情况下，Ray Task 的资源需求相对明确，而 Ray Actor 默认 CPU 资源需求是 0 个，如果不做额外设置，造成一种 Ray Actor 不需要计算资源的假象，导致大量 Actor 被调度到同一个计算节点上。为了更好地控制资源使用并避免潜在的风险，建议在定义 Task 或 Actor 时指定所需的计算资源数量。具体来说，使用 `ray.remote()` 修饰函数或类时，可以通过传递 `num_cpus` 和 `num_gpus` 参数来指定 Task 和 Actor 所需的计算资源。

```
@ray.remote(num_cpus=4)
def func():
    ...

@ray.remote(num_cpus=16, num_gpus=1)
class Actor:
    pass
```

或者调用 `task.options()` 或 `actor.options()` 来指定某个具体计算任务所需的资源，其中 `task` 是经过 `ray.remote()` 修饰的分布式函数，`actor` 是经过 `ray.remote()` 修饰的分布式类的实例。

```
func.options(num_cpus=4).remote()
```

## 其他资源

除了通用的 CPU、GPU 外，Ray 也支持很多其他类型计算资源，比如各类加速器。可以使用 `--resources={"special_hardware": 1}` 这样的键值对来管理这些计算资源。使用方式与 `num_gpus` 管理 GPU 资源相似。比如 Google 的 TPU：`resources={"TPU": 2}`和华为的昇腾：`resources={"NPU": 2}`。某集群 CPU 既有 x86 架构，也有 ARM 架构，对于 ARM 的节点可以这样定义：`resources={"arm64": 1}`。

## 自动缩放

Ray 集群可以自动缩放，主要面向以下场景：

* 当 Ray 集群的资源不够时，创建新的工作节点。
* 当某个工作节点闲置或者无法启动，将该工作节点关闭。

自动缩放主要满足 Task 或 Actor 代码中定义的计算资源请求（比如，`task.options()` 请求的计算资源），而不是根据计算节点的资源实际利用情况自动缩放。

## Placement Group

关于计算资源和集群的配置，Ray提供了一个名为Placement Group的功能，中文可以理解为“资源组”。Placement Group允许用户以**原子地**（Atomically）使用集群上多个节点的计算资源。所谓原子地，是指资源要么全部分配给用户，要么完全不分配，不会出现只分配部分资源的情况。

Placement Group 主要适用于以下场景：

* 组调度（Gang Scheduling）：一个作业需要一组资源，这些资源需要协同工作以完成任务。要么分配，要么不分配。如果只分配给这个作业部分资源，将无法完成整个任务。例如，在大规模分布式训练中，可能需要多台计算节点和多块GPU，这时可以在Ray集群中申请并分配这些资源。

* 负载均衡：作业需要在多个节点上进行负载均衡，每个节点承担一小部分任务。Placement Group可以确保作业尽量分散到多个计算节点上。例如，在分布式推理场景中，如果一个作业需要8块GPU，每个GPU负责加载模型并独立进行推理，为了实现负载均衡，应该将作业调度到8个计算节点上，每个节点使用1块GPU。这样做的好处是，如果一个节点发生故障，不会导致整个推理服务不可用，因为其他节点仍然可以继续工作。

Placement Group 有几个关键概念：

* 资源包（Bundle）：Bundle 一个键值对，用来定义所需的计算资源，比如 `{"CPU": 2}`，或 `{"CPU": 8, "GPU": 4}`。一个 Bundle 必须可以调度到单个计算节点；比如，一个计算节点只有 8 块 GPU，`{"GPU": 10}` 这样的 Bundle 是不合理的。
* 资源组（Placement Group）：Placement Group 是一组 Bundle。比如，`{"CPU": 8} * 4` 会向 Ray 集群申请 4 个 Bundle，每个 Bundle 预留 8 个 CPU。多个 Bundle 的调度会遵循一些调度策略。Placement Group 被 Ray 集群创建后，可被用来运行 Ray Task 和 Ray Actor。

我们可以使用 [`placement_group()`](https://docs.ray.io/en/latest/ray-core/api/doc/ray.util.placement_group.html) 创建 Placement Group。`placement_group()` 是异步的，如果需要等待创建成功，需要调用 [`PlacementGroup.ready()`](https://docs.ray.io/en/latest/ray-core/api/doc/ray.util.placement_group.PlacementGroup.ready.html)。

某个 Ray Task 或 Ray Actor 希望调度到 Placement Group 上，可以在 `options(scheduling_strategy=PlacementGroupSchedulingStrategy(...))` 中设定。

下面是一个完整的例子，运行这个例子之前，提前创建好了有多块 GPU 的 Ray 集群，如果没有 GPU，也可以改为 CPU。

```python
from ray.util.placement_group import (
    placement_group,
    placement_group_table,
    remove_placement_group,
)
from ray.util.scheduling_strategies import PlacementGroupSchedulingStrategy
import ray

ray.init()

print('''Available Resources: {}'''.format(ray.available_resources()))

@ray.remote(num_gpus=2)
def gpu_task():
    print("GPU ids: {}".format(ray.get_runtime_context().get_accelerator_ids()["GPU"]))

# 创建 Placement Group
pg = placement_group([{"CPU": 16, "GPU": 2}])

# 等待 Placement Group 创建成功
ray.get(pg.ready(), timeout=10)
# 也可以使用 ray.wait
ready, unready = ray.wait([pg.ready()], timeout=10)

print('''Placement Group: {}'''.format(placement_group_table(pg)))

# 将 Ray Task 调度到这个 Placement Group
ray.get(gpu_task.options(
    scheduling_strategy=PlacementGroupSchedulingStrategy(placement_group=pg)
).remote())

# 删除这个 Placement Group
remove_placement_group(pg)
```

创建 Placement Group 的 `placement_group()` 方法还接收 `strategy` 参数，用来设定不同的调度策略：或者是让这些预留资源尽量集中到少数计算节点上，或者是让这些预留资源尽量分散到多个计算节点。共有如下策略：

* `STRICT_PACK`：所有 Bundle 都必须调度到单个计算节点。
* `PACK`：所有 Bundle 优先调度到单个计算节点，如果无法满足条件，再调度到其他计算节点，如 {numref}`fig-ray-pg-pack` 所示。`PACK` 是默认的调度策略。
* `STRICT_SPREAD`：每个 Bundle 必须调度到不同的计算节点。
* `SPREAD`：每个 Bundle 优先调度到不同的计算节点，如果无法满足条件，有些 Bundle 可以共用一个计算节点，如 {numref}`fig-ray-pg-spread` 所示。

```{figure} ../img/ch-ray-cluster/pg-pack.svg
---
width: 600px
name: fig-ray-pg-pack
---
`PACK` 策略优先将所有 Bundle 调度到单个计算节点。
```

由于计算尽量调度到了少数计算节点，`STRICT_PACK` 和 `PACK` 的调度策略保证了数据的局部性（Locality），计算任务可以快速访问本地的数据。

```{figure} ../img/ch-ray-cluster/pg-spread.svg
---
width: 600px
name: fig-ray-pg-spread
---
`SPREAD` 策略优先将每个 Bundle 调度到不同的计算节点。
```

`STRICT_SPREAD` 和 `SPREAD` 的调度策略使得计算更好地负载均衡。

:::{note}
多个 Ray Task 或 Actor 可以运行在同一个 Bundle 上，任何使用同一个 Bundle 的 Task 或 Actor 将一直运行在该计算节点上。 
:::
