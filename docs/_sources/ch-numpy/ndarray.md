# ndarray

NumPy 最核心的数据结构是多维数组（N-dimensional Array）： `ndarray`。 `ndarray` 是由同一数据类型的数据组成的数组列表。

```python
import numpy as np
```

### 创建 ndarray

`array` 函数接收来自原生 Python 的各类数据，如列表、元组等，并转化为 `ndarray`；`array` 函数也可以接收一个 NumPy 的 `ndarray`。数组中的数据类型必须是一致的。

```python
# 列表 list
ar1 = np.array([1,2,3,4])
ar1
```

```python
# 元组 tuple
ar2 = np.array((1,2,3,4))
ar2
```

### 数据类型：dtype

在进一步深入了解各种创建 `ndarray` 的方式之前，我们需要了解一下数据类型的基础知识。计算机无法直接表征数值，其底层基于二进制表示数值，整数和浮点数（其实就是小数，计算机科学中一般称小数为浮点数）基于科学计数法，字符串是一个从整数到字符的映射。 NumPy 提供了不同的数据类型 `dtype`，不同的 `dtype` 所能表示的区间范围不同。比如，同为整数，就有以下几种类型，其所表示的数值区间差异较大。

| dtype    	| 区间                     	|
|----------	|-----------------------	|
| np.int8  	| -128 ~ 127            	|
| np.int16 	| -32768 ~ 32767        	|
| np.int32 	| $-2.1*10^9 \sim 2.1*10 ^9$ 	|

NumPy 所支持的数据类型主要有：

* `np.bool_` ：布尔类型
* `np.number` ：又细分为整数（比如 `np.int8` 等）和浮点类型（`np.float32` 等）。
* `np.datetime64`：表示日期的数据类型
* `np.character`：字符串类型

这些数据类型往往都带有一个数字，比如 `np.int8`，数字表示这个数据类型占用了多少个比特（bit）的存储空间。1 个 bit 为一个 0/1 二进制。8 bit = 1 byte，即 8 比特位等于 1 个字节。

根据上表，整数占用的存储空间越大，所能表示的数值范围越大。当我们编写简单的程序时，数值范围一般不会出现问题，但是当我们编写复杂的科学计算程序时，数值范围决定了计算的精度。例如，`np.int8` 只能表示 -128 ~ 127 范围的数值，超过这个数值的数字，如何被 `np.int8` 表示，存在较大不确定性，进而造成程序运行不准确。

占用的 bit 越多，数据越精准，但也会使得对内存消耗越大。选择合适的数据类型有助于节省内存。刚刚接触数据类型的朋友，对于如何选择合适数据类型并不熟悉。大概可以按照如下准则：

* 整数类型默认是 `np.int64`，但很多应用 `np.32` 就足够了。
* 浮点数类型一般科学计算应用都使用 `np.float64`，深度学习类应用使用 `np.float32` 或者甚至更小的数据类型也足够了。

### 创建特定的 ndarray

#### arange() 与 linspace()

`arange` 和 `linspace` 函数可用于生成一个数值数组。数值从区间为 $[start,stop)$ 中选择，一般从 `start` 开始，到 `stop` 结束，在这个区间内生成一系列值。

`arange` 函数的常见形式：

* `arange(stop)`
* `arange(start, stop)`
* `arange(start, stop, step)`

其中，`step` 用于指定数值之间的间隔，默认为 1。

```python
# 以下两种方式等效
np.arange(10)
np.arange(stop=10)
```

`linspace` 函数生成 `num` 个均匀间隔的数值，也就是创建一个等差数列。

常见形式：`linspace(start, stop, num)`。

```python
# 生成在 1 和 5 之间 5 个均匀间隔的数组
a = np.linspace(1,5,5)
a
```

#### ones() 与 ones_like()

`np.ones(shape)` 生成 `shape` 大小的、全为 1 数组。例如，生成 $3 \times 3 \times 6$ 的高维数组。

```python
np.ones((2,3,4), dtype=np.float32)
```

如果已经有一个多维数组 `a`，我们想根据这个数组 `a` 的形状生成一个全为 1 的数组：

```python
np.ones_like(a)
```

#### zeros() 与 zeros_like()

`np.zeros()` 与 `np.ones()` 类似。`np.zeros(shape)` 生成 `shape` 大小的、全为 0 的数组。

```python
np.zeros((2,3,4))
```

如果已经有一个多维数组 `a`，我们想根据这个数组 `a` 的形状生成一个全为 0 的数组：

```python
np.zeros_like(a)
```

#### full() 与 full_like()

`np.full(shape,val)` 生成 `shape` 大小的、全为 `val` 的数组，即数组中每个元素值都是 `val`。

```python
np.full((2,3,4), 6)
```

根据数组 `a` 的形状生成一个数组，元素值全为 `val`：

```python
np.full_like(a, 6)
```

#### eye()

np.eye(n) 创建一个 $n \times n$ 单位矩阵，对角线为 1，其余为 0。

```python
np.eye(3)
```

### 常用属性

直接打印一个 `ndarray` 可以看到它的值、`dtype` 等属性。

```python
ar = np.array([[1,1,2,3,],
               [4,5,6,7],
               [8,9,10,11]])
ar
```

或者打印某些具体的属性。

* ndim：多维数组的秩，或者说轴的数量，或者说数组有多少维度

```python
ar.ndim
```

* 数组的尺度

```python
ar.shape
```

* 数组中元素的个数

```python
ar.size
```

* 元素的数据类型

```python
ar.dtype
```

* 每个元素的大小，以字节（Byte）为单位

```python
ar.itemsize
```

### 数组维度变换

另外，我们经常要对数据进行一些变换。

#### 不改变原数组

* `reshape()` 函数

`reshape(shape)` 函数，不改变数组的元素，根据 `shape` 形状，生成一个新的数组。

```python
ar.reshape((2,6))
```

* `flatten()` 函数

`flatten()` 函数，对数组进行降维，将高维数组压缩成一个一维数组。

```python
ar.flatten()
```

#### 改变原数组

* `resize()` 函数

`resize(shape)` 函数，返回一个 `shape` 形状的数组，功能与 `reshape()` 函数一致，但是修改原数组。

提示：当新数组可容纳数据少于原数据，按照原数据选择前 `shape` 个数据；如果多于，则新数组会按照原数组中的数据顺序进行填补。

```python
ar_new = np.resize(ar, (2, 5))
ar_new
```

```python
ar_new = np.resize(ar, (3, 5))
ar_new
```

### 数据类型变换

#### astype()

`astype(new_type)` 函数，对数组的数据类型进行类型变化，基于对原始数据的拷贝创建一个新的数组。比如，将 `np.int` 类型元素修改为 `np.float64` 类型：

```python
new_ar = ar.astype(np.float64)
new_ar
```

### 合并函数

`np.concatenate()` 将两个或者多个数组合并成一个新数组。

```python
b = np.linspace(1,9,7)

c = np.concatenate((a,b)) #将 a,b 两个数组合并成为 c
c
```

### ndarray 与 Python 列表的转换

列表作为 Python 中原始的数据类型，运算速度慢于 NumPy。如果需要与原生 Python 语言相适配，需做转换：

```python
ar.tolist()
```

