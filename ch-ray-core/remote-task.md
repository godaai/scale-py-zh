分布式函数
--------

被 Ray 加速的函数又被称为 Task。Ray Task 是无状态的，无状态的意思是的执行只依赖函数的输入和输出，不依赖其他第三方的中间变量。

### 顺序执行与分布式执行

一个原生的 Python 函数如果使用 `for` 循环多次执行，将以顺序的方式，依次执行，如 :numref:`serial-timeline` 所示。

![顺序执行的时间轴示意图](../img/ch-ray-core/serial-timeline.png)
:width:`800px`
:label:`serial-timeline`

与原生 Python 函数顺序不同的是，Ray 可以将函数的执行分布式到集群中的多个计算节点上，如 :numref:`distributed-timeline` 所示。

![分布式执行的时间轴示意图](../img/ch-ray-core/distributed-timeline.png)
:width:`800px`
:label:`distributed-timeline`

接下来将以三个案例来演示如何将 Python 函数横向扩展到 Ray 集群上：

* 生成斐波那契数列
* 使用蒙特卡洛方法计算 $\pi$
* 分布式图片处理


```{.python .input}
import logging
import math
import os
import random
import time
from pathlib import Path
from typing import List, Tuple
import numpy as np
import pandas as pd
import ray
import tqdm
```

### 启动 Ray 集群

在正式使用 Ray 的分布式功能之前，首先要启动一个 Ray 集群。启动 Ray 集群的方式有很多种，我们可以使用 `ray.init()` 函数，先在自己的个人电脑上启动一个 Ray 集群，以便后续的演示。


```{.python .input}
if ray.is_initialized:
    ray.shutdown()
ray.init(logging_level=logging.ERROR)
```

### 案例1：斐波那契数列

接下来，我们用斐波那契数列的案例来演示如何使用 Ray 对 Python 函数进行分布式的扩展。

斐波那契数列的第 $n$ 项 $F_n$ 可以由它前面的两个数 $F_{n-1}$ 和 $F_{n-2}$ 计算得到。用形式化的数学公式定义为：

$$
F_n = F_{n-1} + F_{n-2}
$$

其中，$F_0 = 0$，$F_1 = 1$。

下面我们使用原生的 Python 定义一个斐波那契函数。


```{.python .input}
SEQUENCE_SIZE = 200000

def generate_fibonacci(sequence_size):
    fibonacci = []
    for i in range(0, sequence_size):
        if i < 2:
            fibonacci.append(i)
            continue
        fibonacci.append(fibonacci[i-1] + fibonacci[i-2])
    return len(fibonacci)
```

如果我们想让这个 Python 函数被 Ray 分布式执行，只需要在函数上增加一个 `@ray.remote` 装饰器。


```{.python .input}
# 在函数上增加一个 @ray.remote 装饰器
@ray.remote
def generate_fibonacci_distributed(sequence_size):
    return generate_fibonacci(sequence_size)
```

作为 Ray 的使用者，我们不需要关心 Task 在 Ray 集群中是如何被分布式执行的，也不需要了解这个 Task 被调度到哪些计算节点。所有这些分布式执行的细节都被 Ray 所隐藏，或者说 Ray 帮我们做了底层的分布式与调度这些工作。

我们比较一下顺序执行与分布式执行的效率与耗时。`os.cpu_count()` 可以得到当前个人电脑上的 CPU 核心数。顺序执行的代码使用 `for` 循环，多次调用生成斐波那契数列的函数。


```{.python .input}
# 顺序执行
def run_local(sequence_size):
    results = [generate_fibonacci(sequence_size) for _ in range(os.cpu_count())]
    return results
```

使用 Ray 进行分布式扩展，函数可并行地在多个 CPU 核心上执行。


```{.python .input}
# 使用 Ray 进行分布式扩展
def run_remote(sequence_size):
    results = ray.get([generate_fibonacci_distributed.remote(sequence_size) for _ in range(os.cpu_count())])
    return results
```

```{.python .input}
start = time.time()
run_local(SEQUENCE_SIZE)
end = time.time()
elapsed_fib_serial = end - start
print(f"Serial | elapsed: {elapsed_fib_serial:.2f} sec")

start = time.time()
run_remote(SEQUENCE_SIZE)
end = time.time()
elapsed_fib_dist = end - start
print(f"Distributed | elapsed: {elapsed_fib_dist:.2f} sec")
```

这个例子中，计算复杂度不够大，你可以试着将 `SEQUENCE_SIZE` 改为更大的值，对比一下性能。

### 原生 Python 函数与 Ray 的区别

需要注意的是，使用 Ray 与原生 Python 函数稍有区别，主要体现在：

* 函数调用方式

原生 Python 函数，使用 `func_name()` 调用。在使用 Ray 是，函数定义需要增加 `@ray.remote` 装饰器，调用时需要使用 `func_name.remote()` 的形式。

* 返回值

调用一个原生 Python 函数 `func_name()`，即可得到函数的返回值。在使用 Ray 时，`func_name.remote()` 返回值是 `ray.ObjectRef` 类型的对象，`ray.ObjectRef` 并不是一个具体的值，而是一个 Future（尚未完成但未来会完成的计算），需要使用 `ray.get()` 函数获取该调用的实际返回值。

* 执行方式

原生 Python 函数 `func_name()` 的调用是同步执行的，或者说等待结果返回才进行后续计算，又或者说这个调用是阻塞的。一个 Ray 函数`func_name.remote()` 是异步执行的，或者说调用者不需要等待这个函数的计算真正执行完， Ray 就立即返回了一个 `ray.ObjectRef`，函数的计算是在后台某个计算节点上执行的。`ray.get(ObjectRef)` 会等待后台计算结果执行完，将结果返回给调用者。`ray.get(ObjectRef)` 是一个一个阻塞调用。

### 案例2：蒙特卡洛估计 $\pi$

接下来我们使用蒙特卡洛方法来估计 $\pi$。如 :numref:`square-circle`: 我们在一个 $2 \times 2$ 的正方形中随机撒点，正方形内有一个半径为1的圆。所撒的点以一定概率落在圆内，假定我们已知落在圆内的概率是 $\frac{\pi}{4}$，我们可以根据随机撒点的概率情况推算出 $\pi$ 的值。根据概率论相关知识，撒的点越多，概率越接近真实值。

![在正方形内随机撒点，这些点有一定概率落在圆内](../img/ch-ray-core/square-circle.png)
:width:`800px`
:label:`square-circle`


```{.python .input}
NUM_SAMPLING_TASKS = os.cpu_count()
NUM_SAMPLES_PER_TASK = 10_000_000
TOTAL_NUM_SAMPLES = NUM_SAMPLING_TASKS * NUM_SAMPLES_PER_TASK
```

我们定义一个 Python 原生函数，计算落在圆内的概率。我们共随机采样 `num_samples` 次，或者说一共撒 `num_samples` 个点。每次撒点其实就是对横纵坐标 `x` 和 `y` 生成 $[-1, 1]$ 区间内的随机值。如果该点在圆内，则该点距圆心（坐标轴原点）距离小于等于1。math 库中的 [math.hypot](https://docs.python.org/3/library/math.html#math.hypot) 可以计算距离。


```{.python .input}
def sampling_task(num_samples: int, task_id: int, verbose=True) -> int:
    num_inside = 0
    for i in range(num_samples):
        x, y = random.uniform(-1, 1), random.uniform(-1, 1)
        # 判断点在圆内
        if math.hypot(x, y) <= 1:
            num_inside += 1
    if verbose:
        print(f"Task id: {task_id} | Samples in the circle: {num_inside}")
    return num_inside
```

我们定义一个顺序执行的 Python 原生函数，共顺序调用 `NUM_SAMPLING_TASKS` 次。


```{.python .input}
def run_serial(sample_size) -> List[int]:
    results = [sampling_task(sample_size, i+1) for i in range(NUM_SAMPLING_TASKS)]
    return results
```

我们再定义一个 Ray Task：只需要增加 `@ray.remote` 装饰器。记得 Ray Task 是异步执行的，Ray Task 调用之后会立即返回一个 Future ObjectRef，需要使用 `ray.get()` 获取实际计算结果。`ray.get()` 会等待计算结束，并返回实际结果。


```{.python .input}
@ray.remote
def sample_task_distribute(sample_size, i) -> object:
    return sampling_task(sample_size, i)

def run_disributed(sample_size) -> List[int]:
    results = ray.get([
            sample_task_distribute.remote(sample_size, i+1) for i in range(NUM_SAMPLING_TASKS)
        ])
    return results
```

以上两类函数获取了落在圆内的概率，再计算 $\pi$：


```{.python .input}
def calculate_pi(results: List[int]) -> float:
    total_num_inside = sum(results)
    pi = (total_num_inside * 4) / TOTAL_NUM_SAMPLES
    return pi
```

顺序执行与 Ray 分布式执行执行的耗时对比：

```{.python .input}

start = time.time()
results = run_serial(NUM_SAMPLES_PER_TASK)
pi = calculate_pi(results)
end = time.time()
elapsed_pi_serial = end - start
print(f"Serial | estimated value of π is: {pi:5f}, elapsed: {elapsed_pi_serial:.2f} sec")

start = time.time()
results = run_disributed(NUM_SAMPLES_PER_TASK)
pi = calculate_pi(results)
end = time.time()
elapsed_pi_dist = end - start
print(f"Distributed | estimated value of π is: {pi:5f}, elapsed: {elapsed_pi_dist:.2f} sec")
```

### 案例3：分布式图片处理


接下来我们模拟一个更加计算密集的分布式图片预处理的任务。所处理内容均为高清像素图片，大概3-5MB。这些图片数据预处理工作在当前人工智能场景下非常普遍：

* 使用 PIL 库加载图片，并对图片进行模糊（Blur）处理。
* 使用 PyTorch 的 `torchvision` 库中的预处理工具，处理后的图片被转换成 `Tensor`。
* 对 `Tensor` 进行矩阵乘法等计算。

```{.python .input}
import requests

import matplotlib.pyplot as plt 

from PIL import Image
import torch
from torchvision import transforms as T

URLS = [
     'https://images.pexels.com/photos/305821/pexels-photo-305821.jpeg',
     'https://images.pexels.com/photos/509922/pexels-photo-509922.jpeg',
     'https://images.pexels.com/photos/325812/pexels-photo-325812.jpeg',
     'https://images.pexels.com/photos/1252814/pexels-photo-1252814.jpeg',
     'https://images.pexels.com/photos/1420709/pexels-photo-1420709.jpeg',
     'https://images.pexels.com/photos/963486/pexels-photo-963486.jpeg',
     'https://images.pexels.com/photos/1557183/pexels-photo-1557183.jpeg',
     'https://images.pexels.com/photos/3023211/pexels-photo-3023211.jpeg',
     'https://images.pexels.com/photos/1031641/pexels-photo-1031641.jpeg',
     'https://images.pexels.com/photos/439227/pexels-photo-439227.jpeg',
     'https://images.pexels.com/photos/696644/pexels-photo-696644.jpeg',
     'https://images.pexels.com/photos/911254/pexels-photo-911254.jpeg',
     'https://images.pexels.com/photos/1001990/pexels-photo-1001990.jpeg',
     'https://images.pexels.com/photos/3518623/pexels-photo-3518623.jpeg',
     'https://images.pexels.com/photos/916044/pexels-photo-916044.jpeg',
     'https://images.pexels.com/photos/2253879/pexels-photo-2253879.jpeg',
     'https://images.pexels.com/photos/3316918/pexels-photo-3316918.jpeg',
     'https://images.pexels.com/photos/942317/pexels-photo-942317.jpeg',
     'https://images.pexels.com/photos/1090638/pexels-photo-1090638.jpeg',
     'https://images.pexels.com/photos/1279813/pexels-photo-1279813.jpeg',
     'https://images.pexels.com/photos/434645/pexels-photo-434645.jpeg',
     'https://images.pexels.com/photos/1571460/pexels-photo-1571460.jpeg',
     'https://images.pexels.com/photos/1080696/pexels-photo-1080696.jpeg',
     'https://images.pexels.com/photos/271816/pexels-photo-271816.jpeg',
     'https://images.pexels.com/photos/421927/pexels-photo-421927.jpeg',
     'https://images.pexels.com/photos/302428/pexels-photo-302428.jpeg',
     'https://images.pexels.com/photos/443383/pexels-photo-443383.jpeg',
     'https://images.pexels.com/photos/3685175/pexels-photo-3685175.jpeg',
     'https://images.pexels.com/photos/2885578/pexels-photo-2885578.jpeg',
     'https://images.pexels.com/photos/3530116/pexels-photo-3530116.jpeg',
     'https://images.pexels.com/photos/9668911/pexels-photo-9668911.jpeg',
     'https://images.pexels.com/photos/14704971/pexels-photo-14704971.jpeg',
     'https://images.pexels.com/photos/13865510/pexels-photo-13865510.jpeg',
     'https://images.pexels.com/photos/6607387/pexels-photo-6607387.jpeg',
     'https://images.pexels.com/photos/13716813/pexels-photo-13716813.jpeg',
     'https://images.pexels.com/photos/14690500/pexels-photo-14690500.jpeg',
     'https://images.pexels.com/photos/14690501/pexels-photo-14690501.jpeg',
     'https://images.pexels.com/photos/14615366/pexels-photo-14615366.jpeg',
     'https://images.pexels.com/photos/14344696/pexels-photo-14344696.jpeg',
     'https://images.pexels.com/photos/14661919/pexels-photo-14661919.jpeg',
     'https://images.pexels.com/photos/5977791/pexels-photo-5977791.jpeg',
     'https://images.pexels.com/photos/5211747/pexels-photo-5211747.jpeg',
     'https://images.pexels.com/photos/5995657/pexels-photo-5995657.jpeg',
     'https://images.pexels.com/photos/8574183/pexels-photo-8574183.jpeg',
     'https://images.pexels.com/photos/14690503/pexels-photo-14690503.jpeg',
     'https://images.pexels.com/photos/2100941/pexels-photo-2100941.jpeg',
     'https://images.pexels.com/photos/210019/pexels-photo-210019.jpeg',
     'https://images.pexels.com/photos/112460/pexels-photo-112460.jpeg',
     'https://images.pexels.com/photos/116675/pexels-photo-116675.jpeg',
     'https://images.pexels.com/photos/3586966/pexels-photo-3586966.jpeg',
     'https://images.pexels.com/photos/313782/pexels-photo-313782.jpeg',
     'https://www.nasa.gov/centers/stennis/images/content/702979main_SSC-2012-01487.jpg',
     'https://live.staticflickr.com/2443/3984080835_71b0426844_b.jpg',
     'https://www.aero.jaxa.jp/eng/facilities/aeroengine/images/th_aeroengine05.jpg',
     'https://images.pexels.com/photos/370717/pexels-photo-370717.jpeg',
     'https://images.pexels.com/photos/1323550/pexels-photo-1323550.jpeg',
     'https://images.pexels.com/photos/11374974/pexels-photo-11374974.jpeg',
     'https://images.pexels.com/photos/408951/pexels-photo-408951.jpeg',
     'https://images.pexels.com/photos/3889870/pexels-photo-3889870.jpeg',
     'https://images.pexels.com/photos/1774389/pexels-photo-1774389.jpeg',
     'https://images.pexels.com/photos/3889854/pexels-photo-3889854.jpeg',
     'https://images.pexels.com/photos/2196578/pexels-photo-2196578.jpeg',
     'https://images.pexels.com/photos/2885320/pexels-photo-2885320.jpeg',
     'https://images.pexels.com/photos/7189303/pexels-photo-7189303.jpeg',
     'https://images.pexels.com/photos/9697598/pexels-photo-9697598.jpeg',
     'https://images.pexels.com/photos/6431298/pexels-photo-6431298.jpeg',
     'https://images.pexels.com/photos/7131157/pexels-photo-7131157.jpeg',
     'https://images.pexels.com/photos/4840134/pexels-photo-4840134.jpeg',
     'https://images.pexels.com/photos/5359974/pexels-photo-5359974.jpeg',
     'https://images.pexels.com/photos/3889854/pexels-photo-3889854.jpeg',
     'https://images.pexels.com/photos/1753272/pexels-photo-1753272.jpeg',
     'https://images.pexels.com/photos/2328863/pexels-photo-2328863.jpeg',
     'https://images.pexels.com/photos/6102161/pexels-photo-6102161.jpeg',
     'https://images.pexels.com/photos/6101986/pexels-photo-6101986.jpeg',
     'https://images.pexels.com/photos/3334492/pexels-photo-3334492.jpeg',
     'https://images.pexels.com/photos/5708915/pexels-photo-5708915.jpeg',
     'https://images.pexels.com/photos/5708913/pexels-photo-5708913.jpeg',
     'https://images.pexels.com/photos/6102436/pexels-photo-6102436.jpeg',
     'https://images.pexels.com/photos/6102144/pexels-photo-6102144.jpeg',
     'https://images.pexels.com/photos/6102003/pexels-photo-6102003.jpeg',
     'https://images.pexels.com/photos/6194087/pexels-photo-6194087.jpeg',
     'https://images.pexels.com/photos/5847900/pexels-photo-5847900.jpeg',
     'https://images.pexels.com/photos/1671479/pexels-photo-1671479.jpeg',
     'https://images.pexels.com/photos/3335507/pexels-photo-3335507.jpeg',
     'https://images.pexels.com/photos/6102522/pexels-photo-6102522.jpeg',
     'https://images.pexels.com/photos/6211095/pexels-photo-6211095.jpeg',
     'https://images.pexels.com/photos/720347/pexels-photo-720347.jpeg',
     'https://images.pexels.com/photos/3516015/pexels-photo-3516015.jpeg',
     'https://images.pexels.com/photos/3325717/pexels-photo-3325717.jpeg',
     'https://images.pexels.com/photos/849835/pexels-photo-849835.jpeg',
     'https://images.pexels.com/photos/302743/pexels-photo-302743.jpeg',
     'https://images.pexels.com/photos/167699/pexels-photo-167699.jpeg',
     'https://images.pexels.com/photos/259620/pexels-photo-259620.jpeg',
     'https://images.pexels.com/photos/300857/pexels-photo-300857.jpeg',
     'https://images.pexels.com/photos/789380/pexels-photo-789380.jpeg',
     'https://images.pexels.com/photos/735987/pexels-photo-735987.jpeg',
     'https://images.pexels.com/photos/572897/pexels-photo-572897.jpeg',
     'https://images.pexels.com/photos/300857/pexels-photo-300857.jpeg',
     'https://images.pexels.com/photos/760971/pexels-photo-760971.jpeg',
     'https://images.pexels.com/photos/789382/pexels-photo-789382.jpeg',
     'https://images.pexels.com/photos/33041/antelope-canyon-lower-canyon-arizona.jpg',
     'https://images.pexels.com/photos/1004665/pexels-photo-1004665.jpeg'
]

# 图片将下载到该文件夹
DATA_DIR = Path(os.getcwd() + "/function-task-images")

THUMB_SIZE = (64, 64)
                                                                   
def display_random_images(image_list: List[str], n: int=3) -> None:
    """
    随机选择图片并展示出来
    """
    random_samples_idx = random.sample(range(len(image_list)), k=n)
    plt.figure(figsize=(16, 8))
    for i, targ_sample in enumerate(random_samples_idx):
        plt.subplot(1, n, i+1)
        img = Image.open(image_list[targ_sample])
        img_as_array = np.asarray(img)
        plt.imshow(img_as_array)
        title = f"\nshape: {img.size}"
        plt.axis("off")
        plt.title(title)
    plt.show() 

def download_images(url: str, data_dir: str) -> None:
    """
    下载图片
    """
    img_data = requests.get(url).content
    img_name = url.split("/")[4]
    img_name = f"{data_dir}/{img_name}.jpg"
    with open(img_name, 'wb+') as f:
        f.write(img_data) 

@ray.remote
def augment_image_distributed(image_ref: object, fetch_image) -> List[object]:
    return transform_image(image_ref, fetch_image=fetch_image)

def run_serially(img_list_refs: List) -> List[Tuple[int, float]]:
    transform_results = [transform_image(image_ref, fetch_image=True) for image_ref in tqdm.tqdm(img_list_refs)]
    return transform_results

def run_distributed(img_list_refs:List[object]) ->  List[Tuple[int, float]]:
    return ray.get([augment_image_distributed.remote(img, False) for img in tqdm.tqdm(img_list_refs)])
```

我们将图片放在 Ray 的分布式对象存储中（Object Store），如 :numref:`put-get-object-store` 分布式的 Object Store 可以允许集群上多个计算节点共享数据。这里使用 `ray.get()` 和 `ray.put()` 向 Object Store 上读写数据，我们将在 :numref:`object-store` 中详细解释 Object Store 的使用方法。

![Object Store 在多个计算节点上共享数据](../img/ch-ray-core/put-get-object-store.png)
:width:`800px`
:label:`put-get-object-store`

```{.python .input}
def insert_into_object_store(img_name: str):
    """
    将图片插入 Object Store
    """
    
    img = Image.open(img_name)
    img_ref = ray.put(img)
    return img_ref
```

计算密集型函数 `transform_image`，模拟了深度学习中经常使用的图片数据预处理操作。对于顺序执行部分，我们需要使用 `ray.get()` 从 Object Store 中将图片数据拉取。

```{.python .input}
def transform_image(img_ref: object, fetch_image=True, verbose=False):
    """
    图片预处理函数，模拟图片读取，torchvision 数据预处理和 Tensor 矩阵乘法等计算密集型任务
    """
    
    # 顺序执行时，需要将图片从 Ojbect Store 中拉取
    if fetch_image:
        orig_img = ray.get(img_ref)
    else:
        orig_img = img_ref
    before_shape = orig_img.size
    
    # torchvision 提供的一系列数据预处理操作
    gray_img = T.Grayscale()(orig_img)

    cropper = T.RandomCrop(size=(224, 224))
    crops = [cropper(orig_img) for _ in range(4)]

    augmentor = T.TrivialAugmentWide(num_magnitude_bins=31)
    augmented_img = augmentor(orig_img)

    # 将图片转换成 Tensor
    tensor = torch.tensor(np.asarray(augmented_img))
    t_tensor = torch.transpose(tensor, 0, 1)

    # 进行矩阵乘法等计算密集型任务
    random.seed(42)
    for _ in range(3):
        tensor.pow(3).sum()
        t_tensor.pow(3).sum()
        torch.mul(tensor, random.randint(2, 10))
        torch.mul(t_tensor, random.randint(2, 10))
        torch.mul(tensor, tensor)
        torch.mul(t_tensor, t_tensor)

    # 将数据增广后的图片转换为缩略图
    augmented_img.thumbnail(THUMB_SIZE)
    after_shape = augmented_img.size
    if verbose:
        print(f"original shape:{before_shape}, image tensor shape:{tensor.size()} transpose shape:{t_tensor.size()}")

    return before_shape, after_shape
```

下载并随机展示图片：

```{.python .input}
if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)
    print(f"downloading images ...")
    for url in tqdm.tqdm(URLS):
        download_images(url, DATA_DIR)

image_list = list(DATA_DIR.glob("*.jpg"))
images_list_refs = [insert_into_object_store(image) for 
                  image in image_list]

display_random_images(image_list, n=5)
```

比较顺序执行与分布式执行的耗时：

```{.python .input}

# 顺序执行
print(f"\nRunning {len(images_list_refs)} images serially....")
start = time.time()
serial_results = run_serially(images_list_refs)
end = time.time()
elapsed_img_serial = end - start
print(f"Serial transformations of {len(images_list_refs)} images: {elapsed_img_serial:.2f} sec")

# 使用 Ray 分布式执行
print(f"\nRunning {len(images_list_refs)} images distributed....")
start = time.time()
distributed_results = run_distributed(images_list_refs)
end = time.time()
elapsed_img_dist = end - start
print(f"Distributed transformations of {len(images_list_refs)} images: {elapsed_img_dist:.2f} sec")
```

三个案例运行结束，我们比较一下 Ray 的分布式执行效率。

```{.python .input}
from IPython import display
display.set_matplotlib_formats('svg')

data = {'workload': ["fib", "pi", "img"],
        'serial' : [elapsed_fib_serial, elapsed_pi_serial, elapsed_img_serial],
        'distributed': [elapsed_fib_dist, elapsed_pi_dist, elapsed_img_dist]}

df = pd.DataFrame(data)
df.plot(x="workload", y=["serial", "distributed"], kind="bar")
plt.ylabel('Time(sec)', fontsize=12)
plt.xlabel('Workload', fontsize=12)
plt.grid(False)
plt.show()
```

最后还有一个需要注意的地方，当不需要计算时，使用 `ray.shutdown()` 将 Ray 关闭，否则 Ray 进程会一直在你的个人电脑上运行。

```{.python .input}
ray.shutdown()
```
