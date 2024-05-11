(sec-ecosystem)=
# 软件生态与本书内容

## Python 软件生态

Python 已经成为数据科学首选的编程语言。{numref}`fig-python-ecosystem-img` 是一些主流的数据科学工具：

* NumPy 和 pandas 可以进行科学计算和数据处理。
* PyTorch 和 TensorFlow 可以实现神经网络训练和推理。
* scikit-learn 、XGBoost、LightGBM 等库可以实现常见机器学习算法。

```{figure} ../img/ch-data-science/python-ecosystem.svg
---
width: 800px
name: fig-python-ecosystem-img
---
Python 数据科学软件生态
```

## 本书内容

本书假定读者已经对数据科学有所了解，已经使用过 pandas、XGBoost、PyTorch 等 Python 数据科学软件，希望使用一些工具加速数据科学，如果对数据科学不熟悉，可以阅读以下书籍。

* Wes McKinney（pandas 项目发起人）撰写的《利用 Python 进行数据分析》 {cite}`mckinney2022python` 是一本非常优秀的数据科学入门书籍，也是 pandas 框架的入门书籍。
* 周志华老师的《机器学习》 {cite}`zhou2016machine` 是机器学习理论的入门教科书，是了解绝大多数机器学习算法的必备书籍。
* 亚马逊科学家阿斯顿·张、李沐等人的《动手学深度学习》 {cite}`zhang2019dive` 从算法原理到编程实践，深入浅出地讲解了常见人工智能算法及其应用，是入门深度学习的最佳实战书籍。

Dask、Ray、Xorbits 和 mpi4py 是对数据科学生态的拓展，将单机任务横向扩展到集群。这些框架有很多组件，{numref}`tab-lifecycle-module` 概括了这些框架组件所对应的数据科学生命周期、

```{table} 数据科学生命周期与框架组件
:name: tab-lifecycle-module
|生命周期|框架组件|
|---|---|
|数据处理|Dask DataFrame、Dask Array、Ray Data、Modin、Xorbits Data|
|模型训练|Dask-ML、Ray Train、RLib、mpi4py|
|超参数调优|Dask-ML、Ray Tune|
|模型部署|Ray Serve、Xinference|
```