(sec-ray-job)=
# Ray 作业

部署好一个 Ray 集群后，我们就可以向集群上提交作业了。Ray 作业指的是用户编写的，基于 Task、Actor 或者 Ray 各类生态（Ray Train、Ray Tune、Ray Serve、RLlib 等）的具体的计算任务。Ray 集群正在尝试提供多租户的服务，可以同时运行多个用户多种不同类型的计算任务。由于 Ray 集群提供多租户服务的特点，不同的 Ray 作业的源代码、配置文件和软件包环境不一样，因此，在提交作业时除了需要指定当前作业的 `__main__` 函数的入口外，还需要：

* 工作目录：这个作业所需要的 Python 源代码和配置文件
* 软件环境：这个作业所依赖的 Python 软件包和环境变量

向 Ray 集群上提交作业主要有三类方式，使用这三类都需要指定以上作业相关信息。

* Ray Jobs 命令行
* Python Software Development Kit (SDK)
* Ray 客户端

## Ray Jobs 命令行

### `ray job`

Ray Jobs 命令行指的是 `ray job` 一系列操作作业的脚本。在 Python 环境中安装好 Ray 之后（`pip install "ray[default]"`），也会安装命令行工具，其中 `ray job` 负责作业的全生命周期管理。

我们先写好一个基于 Ray 的脚本，放置在当前目录 `./` 下，名为 `scripy.py`：

```python
import os

import ray

ray.init()

print('''This cluster consists of
    {} nodes in total
    {} CPU resources in total
'''.format(len(ray.nodes()), ray.cluster_resources()['CPU']))

@ray.remote
def generate_fibonacci(sequence_size):
    fibonacci = []
    for i in range(0, sequence_size):
        if i < 2:
            fibonacci.append(i)
            continue
        fibonacci.append(fibonacci[i-1] + fibonacci[i-2])
    return len(fibonacci)

sequence_size = 10
results = ray.get([generate_fibonacci.remote(sequence_size) for _ in range(os.cpu_count())])
print(results)
```
使用 `ray job submit` 提交这个作业：

```bash
RAY_ADDRESS='http://127.0.0.1:8265' ray job submit --working-dir ./ -- python script.py
```

`RAY_ADDRESS` 根据头节点的地址来设定，如果只有本地的 Ray 集群，头节点的 IP 地址是 `127.0.0.1`，默认端口是 8265，那么这个地址为 `http://127.0.0.1:8265` ；假如有一个远程的集群，地址修改为远程集群的 IP 或主机名。

Ray Job 命令行将工作目录 `./` 下的源代码打包，将该作业提交到集群上，并打印出下面的信息：

```
Job submission server address: http://127.0.0.1:8265
INFO dashboard_sdk.py:338 -- Uploading package gcs://_ray_pkg_bd62811ee3a826e8.zip.
INFO packaging.py:530 -- Creating a file package for local directory './'.

-------------------------------------------------------
Job 'raysubmit_VTRVfy8VEFY8vCdn' submitted successfully
-------------------------------------------------------
```

`ray job submit` 的格式为：`ray job submit [OPTIONS] ENTRYPOINT...`。 `[OPTIONS]` 可以指定一些参数。 `--working-dir` 为工作目录，Ray 会将该目录下的内容打包，分发到 Ray 集群各个节点。`ENTRYPOINT` 指的是需要执行的 Python 脚本，本例中，是 `python script.py`。我们还可以给这个 Python 脚本传参数，就跟在单机执行 Python 脚本一样：`python script.py --arg=val`。

`--no-wait` 参数可以先提交作业到 Ray 集群，而不是一直等待作业结束。作业的结果可以通过 `ray job logs <jobid>` 查看。

:::{note}
`ENTRYPOINT` 和 `[OPTIONS]` 之间有空格。
:::

### 入口

`ENTRYPOINT` 是程序的入口，在刚才的例子中，程序的入口就是调用 `generate_fibonacci` 的 Ray Task，Ray Task 会被调度到 Ray 集群上。默认情况下，`ENTRYPOINT` 中的入口部分在头节点上运行，因为头节点的资源有限，不能执行各类复杂的计算，只能起到一个入口的作用，各类复杂计算应该在 Task 或 Actor 中执行。默认情况下，无需额外的配置，Ray 会根据 Task 或 Actor 所设置的资源需求，将这些计算调度到计算节点上。但如果 `ENTRYPOINT` 的入口（调用 Task 或 Actor 之前）就使用了各类资源，比如 GPU，那需要给这个入口脚本额外分配资源，需要在 `[OPTIONS]` 中设置 `--entrypoint-num-cpus`、`--entrypoint-num-gpus` 或者 `--entrypoint-resources`。比如，下面的例子分配了 1 个 GPU 给入口。

```
RAY_ADDRESS='http://127.0.0.1:8265' ray job submit --working-dir ./ --entrypoint-num-gpus 1 -- python gpu.py
```

其中 `gpu.py` 代码如下：

```python
import os
import ray

ray.init()

@ray.remote(num_gpus=1)
class GPUActor:
    def ping(self):
        print("GPU ids: {}".format(ray.get_runtime_context().get_accelerator_ids()["GPU"]))
        print("CUDA_VISIBLE_DEVICES: {}".format(os.environ["CUDA_VISIBLE_DEVICES"]))

@ray.remote(num_gpus=1)
def gpu_task():
    print("GPU ids: {}".format(ray.get_runtime_context().get_accelerator_ids()["GPU"]))
    print("CUDA_VISIBLE_DEVICES: {}".format(os.environ["CUDA_VISIBLE_DEVICES"]))

print("ENTRYPOINT CUDA_VISIBLE_DEVICES: {}".format(os.environ["CUDA_VISIBLE_DEVICES"]))
gpu_actor = GPUActor.remote()
ray.get(gpu_actor.ping.remote())
ray.get(gpu_task.remote())
```

调用 Actor 和 Task 之前，Ray 分配了一个 GPU 给程序的入口。调用 Actor 和 Task 之后，又分别给 `gpu_actor` 和 `gpu_task` 分配了 1 个 GPU。

:::{note}
提交作业到一个已有的 Ray 集群上时，`ray.init()` 中不能设置 `num_cpus` 和 `num_gpus` 参数。
:::

### 依赖管理

Ray 集群是多租户的，上面可能运行着不同用户的作业，不同作业对 Python 各个依赖的版本要求不同，Ray 提供了运行时环境的功能，比如在启动这个作业时，设置 `--runtime-env-json`，他是一个 JSON，包括：需要 `pip` 安装的 Python 包，或环境变量（`env_vars`），或工作目录（`working_dir`）。Ray 集群的运行时环境大概原理是为每个作业创建一个独立的虚拟环境（[virtualenv](https://virtualenv.pypa.io/)）。

```json
{
    "pip": ["requests==2.26.0"],
    "env_vars": {"TF_WARNINGS": "none"}
}
```

## Python SDK

Python SDK 的底层原理与命令行相似，只不过将提交作业的各类参数写在 Python 代码中，执行 Python 代码来提交作业。SDK 提供了一个客户端，用户在客户端调用 `ray.job_submission.JobSubmissionClient` 来传递作业参数。

```python
import time
from ray.job_submission import JobSubmissionClient, JobStatus

client = JobSubmissionClient("http://127.0.0.1:8265")
job_id = client.submit_job(
    entrypoint="python script.py",
    runtime_env={"working_dir": "./"}
)
print(job_id)

def wait_until_status(job_id, status_to_wait_for, timeout_seconds=5):
    start = time.time()
    while time.time() - start <= timeout_seconds:
        status = client.get_job_status(job_id)
        print(f"status: {status}")
        if status in status_to_wait_for:
            break
        time.sleep(1)


wait_until_status(job_id, {JobStatus.SUCCEEDED, JobStatus.STOPPED, JobStatus.FAILED})
logs = client.get_job_logs(job_id)
print(logs)
```

[`JobSubmissionClient.submit_job()`](https://docs.ray.io/en/latest/cluster/running-applications/job-submission/doc/ray.job_submission.JobSubmissionClient.submit_job.html) 作业提交是异步的，Ray 会马上返回作业的 ID。如果想要看到作业的运行情况，需要 `wait_until_status()` 函数，不断向 Ray 集群请求，查看该作业的状态。跟命令行类似，`submit_job()` 中传入 `runtime_env` 来指定工作目录或依赖的 Python 包；`entrypoint_num_cpus` 和 `entrypoint_num_gpus` 指定入口所需要的计算资源。

## Ray 客户端

Ray 客户端指的是在 Python 的 `ray.init()` 中直接指定 Ray 集群的地址：`ray.init("ray://<head-node-host>:<port>")`。

:::{note}
注意，这里的 `port` 默认为 10001，或者在 `ray start --head` 时对 `--ray-client-server-port` 进行设置。
:::

客户端可以运行在个人电脑上，用户可以交互地调用集群的计算资源。需要注意的是，客户端的一些功能不如命令行和 SDK 完善，复杂的任务应优先使用命令行或者 SDK。

`ray.init()` 也接收 `runtime_env` 参数，用来指定 Python 包版本或工作目录。跟 Ray Jobs 命令行一样，Ray 会将工作目录中的数据传到 Ray 集群上。

如果客户端与 Ray 集群的连接断开，这个客户端创建的分布式对象或引用都会被销毁。如果客户端和 Ray 集群意外断开，Ray 会在 30 秒后重新连接，重新连接失败后会把各类引用销毁。环境变量 `RAY_CLIENT_RECONNECT_GRACE_PERIOD` 可对这个时间进行自定义。