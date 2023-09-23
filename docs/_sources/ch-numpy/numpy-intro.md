# NumPy 简介

Python 语言其实并不是为科学计算而设计的，到了 2000 年左右，Python 在科学计算领域变得越来越受欢迎，但缺乏一个高效的数组处理工具。Python 的列表（list）虽然灵活，但在处理大型数据集时性能不佳。

NumPy 并不是第一个 Python 科学计算库，它的前身有 Numeric、Numarray 等，并借鉴 Fortran、MATLAB、和 S 语言了优点。经过了一系列的演化发展，Travis Oliphant 在 2005 年创建了 NumPy 项目，并在 2006 年发布了 NumPy 1.0。NumPy 的目标是提供高性能的多维数组对象，以及用于数组操作的丰富函数库。NumPy 引入了 `ndarray` 这一核心数据结构。

自从 NumPy 项目创建以来，它已经成为 Python 科学计算生态系统中的核心组件。许多其他科学计算和数据分析库，如 SciPy、pandas 和 Matplotlib，都构建在 NumPy 之上。

### 安装 pandas

可以使用 `conda` 或者 `pip` 安装：

```bash
pip install numpy -i https://pypi.tuna.tsinghua.edu.cn/simple
```

