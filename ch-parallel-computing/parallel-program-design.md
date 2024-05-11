(sec-parallel-program-design)=
# 并行程序设计方法

## PCAM

如何设计软件和算法，使得程序可以并行运行在多核或者集群上？早在 1995 年，Ian Foster 在其书中提出了 PCAM 方法 {cite}`foster1995designing`，其思想可以用来指导并行算法的设计。PCAM 主要有四个步骤：切分（Partitioning）、通信（Communication）、聚集（Agglomeration）和分发（Mapping）；{numref}`fig-pcam-img` 展示了这四个步骤。

```{figure} ../img/ch-parallel-computing/pcam.svg
---
width: 400px
name: fig-pcam-img
---
PCAM 方法
```

* Partitioning：将整个问题切分为多个子问题或子任务，切分既包括计算部分也包括数据部分。
* Communication：不同子任务之间通信方式，包括通信的数据结构、通信算法。
* Agglomeration：考虑到当前所拥有的硬件性能和编程难度，将上面两步进一步整合，将细粒度的任务整合成更高效的任务。
* Mapping：将整合好的任务分发给多个处理器。

比如，有一个超大矩阵，矩阵大小为 $M \times M$，这个矩阵大到无法放在单个计算节点上计算，现在想得到这个矩阵的最大值。设计并行算法时，可以考虑如下思路：

* 将矩阵切分成子矩阵，每个子矩阵 $m \times m$ 大小，在每台计算节点上执行 `max()` 函数求得子矩阵的最大值。
* 将每个子矩阵的最大值汇集到一个计算节点，再该节点再次执行一下 `max()` 求得整个矩阵的最大值。
* $m \times m$ 大小的子矩阵 `max()` 可以在单个计算节点上运行。
* 将以上计算分发到多个节点。

## 切分方式

设计并行程序最困难也是最关键的部分是如何进行切分，常见的切分方式有：

* 任务并行：一个复杂的程序往往包含多个任务，将不同的任务交给不同的 Worker，如果任务之间没有太多复杂的依赖关系，这种方式可以很好地并发执行。
* 几何分解：所处理的数据结构化，比如矩阵可以根据一维或多维分开，分配给不同的 Worker，刚才提到的对矩阵求最大值就是一个例子。

## 案例：MapReduce

Google 2004 年提出 MapReduce {cite}`dean2004MapReduce`，这是一种典型的大数据并行计算范式。{numref}`fig-map-reduce` 展示了使用 MapReduce 进行词频统计的处理方式。

```{figure} ../img/ch-parallel-computing/map-reduce.svg
---
width: 800px
name: fig-map-reduce
---
MapReduce 进行词频统计
```

MapReduce 中主要涉及四个阶段：

* 切分（Split）：将大数据切分成很多份小数据，每份小数据可以在单个 Worker 上计算。
* 映射（Map）：对每个小数据执行 Map 操作，Map 是一个函数映射，程序员需要自定义 Map 函数，Map 函数输出一个键值对（Key-Value）。在词频统计的例子中，每出现一个词，计 1 次，Key 是词，Value 是 1，表示出现 1 次。
* 交换（Shuffle）：将相同的 Key 归结到相同的 Worker 上。这一步涉及数据交换。词频统计的例子中，将相同的词发送到同一个 Worker 上。
* 聚合（Reduce）：所有相同的 Key 进行聚合操作，程序员需要自定义 Reduce 函数。词频统计的例子中，之前 Shuffle 阶段将已经将相同的 Key 归结到了一起，现在只需要将所有词频求和。

MapReduce 的编程范式深刻影响了 Apache Hadoop、Apache Spark、Dask 等开源项目。