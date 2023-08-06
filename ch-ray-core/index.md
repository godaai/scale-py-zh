Ray Core 简介
------------

Ray 可以将 Python 函数或者类等计算任务横向扩展到多个计算节点上，所有的 Python 计算任务是异步执行的。Ray 一共提供了两个计算接口和一个数据接口，如 :numref:`ray-core-apis` 所示。

* 任务（Task）：面向函数（Function）的接口，用于定义一个函数，该函数可以在集群中分布式地执行。
* 行动者（Actor）：面向类（Class）的接口，用于定义一个类，该类可以在集群中分布式地执行。
* 对象（Object）：分布式的对象，对象不可变（Immutable），用于在 Task 和 Actor 之间传递数据。

![Ray Core 核心API](../img/ch-ray-core/ray-apis.png)
:width:`800px`
:label:`ray-core-apis`

```toc
:maxdepth: 2

remote-function
remote-object
remote-class
```