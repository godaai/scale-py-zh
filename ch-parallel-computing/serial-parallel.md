(sec-serial-parallel)=
# 串行执行与并行执行

如果不对计算任务（Task）进行并行加速，大部分计算任务是串行执行的，即 {numref}`fig-serial-timeline` 所示。这里的 Worker 可以是一个计算核心，也可以是集群中的一个节点。

```{figure} ../img/ch-parallel-computing/serial-timeline.svg
---
width: 800px
name: fig-serial-timeline
---
串行执行的时间轴示意图
```

集群和异构计算提供了更多可利用的计算核心，并行计算将计算任务分布到多个 Worker 上，如 {numref}`fig-distributed-timeline` 所示。无论是在单机多核编程，还是在集群多机，都需要一个调度器（Scheduler）将计算任务分布到不同的 Worker 上。随着更多 Worker 参与，任务总时间缩短，节省的时间可用于其他任务。

```{figure} ../img/ch-parallel-computing/distributed-timeline.svg
---
width: 800px
name: fig-distributed-timeline
---
分布式执行的时间轴示意图
```