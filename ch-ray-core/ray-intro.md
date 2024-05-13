# Ray 简介

Ray 是一个可扩展的计算框架。它最初为强化学习设计，之后逐渐演变成一个面向数据科学和人工智能的框架。
如 {numref}`fig-ray-ecosystem` 所示，当前 Ray 主要由底层的 Ray Core 和上层的各类 Ray AI (Artificial Intelligence) 生态组成：Ray Core 是一系列底层 API, 可以将 Python 函数或者 Python 类等计算任务横向扩展到多个计算节点上；在 Ray Core 之上，Ray 封装了一些面向数据科学和人工智能的库（Ray AI Libraries），可以进行数据的处理（Ray Data）、模型训练（Ray Train）、模型的超参数调优（Ray Tune），模型推理服务（Ray Serve），强化学习（RLib）等。

```{figure} ../img/ch-ray-core/ray.svg
---
width: 800px
name: fig-ray-ecosystem
---
Ray 生态
```

Ray Core 提供的 API 将 Python 任务横向扩展到集群上，最关键的 API 是两个计算接口和一个数据接口，如 {numref}`fig-ray-core-apis` 所示。

* 任务（Task）：面向函数（Function）的接口，用于定义一个函数，该函数可以在集群中分布式地执行。
* 行动者（Actor）：面向类（Class）的接口，用于定义一个类，该类可以在集群中分布式地执行。
* 对象（Object）：分布式的对象，对象不可变（Immutable），用于在 Task 和 Actor 之间传递数据。

上层的各类生态均基于 Ray Core 的这些底层 API，结合各类人工智能应用编写而成。

```{figure} ../img/ch-ray-core/ray-apis.svg
---
width: 800px
name: fig-ray-core-apis
---
Ray Core 核心 API
```