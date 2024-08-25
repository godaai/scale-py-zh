(sec-ray-cluster-resource)=
# Ray 集群

## Ray 集群

如 {numref}`fig-ray-cluster` 所示，Ray 集群由一系列计算节点组成，其中两类关键的节点：头节点（Head）和工作节点（Worker）。这些节点可以部署在虚拟机、容器或者是裸金属服务器上。

```{figure} ../img/ch-ray-cluster/ray-cluster.svg
---
width: 800px
name: fig-ray-cluster
---
Ray 集群由头节点和多个工作节点组成，头节点上运行着一些管理进程。
```

在 Ray 分布式计算环境中，所有节点上都运行着一些关键进程。

* Worker

每个计算节点上运行着一个或多个 Worker 进程，这些进程负责执行计算任务。Worker 进程可以是无状态的，意味着它们可以反复执行 Task 对应的任务；它们也可以是有状态的 Actor，即执行远程类的方法。默认情况下，Worker 的数量等于其所在计算节点的 CPU 核心数。

* Raylet

每个计算节点上运行着一个 Raylet。每个计算节点可能运行多个 Worker 进程，但每个计算节点上只有一个 Raylet 进程，或者说 Raylet 被多个 Worker 进程所共享。Raylet 主要包含两个组件：一个是调度器（Scheduler），它负责资源管理和任务分配；另一个是基于共享内存的对象存储（Shared-memory Object Store），它负责本地数据存储，各个计算节点上的 Object Store 共同构成了 Ray 集群的分布式对象存储。

从 {numref}`fig-ray-cluster` 中也可以看到，头节点还多了：

* Global Control Service（GCS）

GCS 是 Ray 集群的全局元数据管理服务，负责存储和管理诸如哪个 Actor 被分配到哪个计算节点等元数据信息。这些元数据是被所有 Worker 共享的。

* Driver

Driver 用于执行程序的入口点。入口点指的是Python 的   `__main__` 函数。通常，`__main__` 在运行时不应该执行大规模计算，而是负责将 Task 和 Actor 调度到具备足够资源的 Worker 上。

Ray 的头节点还运行着其他一些管理类的服务，比如计算资源自动缩放、作业提交等服务。

## 启动 Ray 集群

之前在 Python 代码中使用 `ray.init()` 方式，仅在本地启动了一个单机的 Ray 集群。实际上，Ray 集群包括头节点和工作节点，应该分别启动。先在头节点启动：

```bash
ray start --head --port=6379
```

它会在该物理节点启动一个头节点进程，默认端口号是 6379，也可以用 `--port` 来指定端口号。执行完上述命令后，命令行会有一些提示，包括当前节点的地址，如何关停。启动工作节点：

```bash
ray start --address=<head-node-address>:<port>
```

将 `<head-node-address>:<port>` 替换为刚刚启动的 Ray 头节点的地址。

此外，Ray 还提供了 `ray up` 这种集群启动命令，它接收 yaml 文件作为参数，在 yaml 文件里定义好头节点地址、工作节点地址。一个文件的样例 [example.yaml](https://raw.githubusercontent.com/ray-project/ray/master/python/ray/autoscaler/local/example-full.yaml)：

```yaml
cluster_name: default

provider:
    type: local
    head_ip: YOUR_HEAD_NODE_HOSTNAME
    worker_ips: [WORKER_NODE_1_HOSTNAME, WORKER_NODE_2_HOSTNAME, ... ]
```

使用下面的命令，它会帮我们启动这个 Ray 集群：

```
ray up example.yaml
```

可以用 `ray status` 命令查看启动的 Ray 集群的状态。

:::{note}
Ray 的头节点暴露了三个端口号，默认分别是 6379, 8265, 10001。启动 Ray 时，设置了 Ray 头节点的端口号，默认为 6379，这个端口号是头节点和工作节点之间通信的端口。Ray 头节点启动后，还提供了一个 Ray 仪表盘端口号，默认为 8265，这个端口号可用来接收 Ray 命令行提交的作业。此外，还有一个端口 `10001`，默认为 `ray.init()` 连接时使用。
:::

以上方法可在多台虚拟机或物理机上部署一个 Ray 集群，Ray 也提供了 Kubernetes 和配套工具，可以支持自动缩放。