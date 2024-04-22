(sec-ray-serve)=
# Ray Serve

一个生产可用的模型推理系统通常有很长的链路：

* 对外服务 API：可能是 HTTP 的，也可能基于远程过程调用协议（Remote Procedure Call，RPC）的。对外服务的 API 又被称为访问入口（Ingress）。其他用户或者程序通过 Ingress 来访问模型推理服务。HTTP 服务可以基于 [FastAPI](https://fastapi.tiangolo.com/)，RPC 可以基于 [gRPC](https://grpc.io/)。
* 模型推理引擎：给定模型和输入，进行模型推理。模型推理引擎可能是成熟的深度学习框架，比如 PyTorch 或者 TensorFlow；可能是针对某个领域的高性能推理框架，比如针对大语言模型的 [vLLM](https://github.com/vllm-project/vllm)，或者是厂商自研的框架。
* 输入输出处理模块：对输入数据进行必要的特征预处理，或对模型输出进行一定的后处理。以输入数据预处理为例，数据可能存储在数据库中，需要经过预处理才能交付给机器学习模型。
* 多模型：大型项目通常需要多个模型共同协作。比如短视频推荐系统有多个模块：从海量视频素材中召回用户最感兴趣的少量内容，使用不同的模型预测用户的点击概率或停留时长，结合多种不同的指标对召回内容进行排序。

Ray Serve 是基于 Ray 的模型推理服务框架。Ray Serve 基于 Ray 的并行能力，解决模型推理中的痛点：

* 底层基于 Ray 的并行计算能力，可封装任何 Python 推理引擎，并支持横向扩展和负载均衡。
* 胶水语言的特性，能够定义复杂的模型推理链路，将不同的数据源、推理引擎和模型粘合在一起，使得开发者进行敏捷开发。
* 集成了常见的 Ingress，比如 FastAPI 和 gRPC。

## 关键概念

Ray Serve 中有两个关键概念：部署（Deployment）和应用程序（Application）。

* [`Application`](https://docs.ray.io/en/latest/serve/api/doc/ray.serve.Application.html) 是一个完整的推理应用。
* [`Deployment`](https://docs.ray.io/en/latest/serve/api/doc/ray.serve.Deployment.html) 可以理解成整个推理应用的某个子模块，比如，对于输入数据进行预处理，或使用机器学习模型进行预测。一个 `Application` 可以有很多个 `Deployment` 组成，每个 `Deployment` 执行某种业务逻辑。
* Ingress 是一种一个特殊的 `Deployment`。它是推理服务的访问入口，所有访问流量都由 Ingress 流入。Ray Serve 的 Ingress 默认使用 [Starlette](https://www.starlette.io/)，也支持 FastAPI 或者 gRPC。

## 案例：大语言模型推理

我们将结合大语言模型推理任务来演示如何使用 Ray Serve。具体而言，我们使用 [Transformers](https://github.com/huggingface/transformers) 来实现聊天功能，Transformers 库是推理引擎，Ray Serve 对 Ingress 等进行了封装。

### 服务端

基于 Transformers 库的模型推理需要加载分词器和模型权重，模型根据输入内容生成回答。如 {numref}`code-llm` 所示，我们先实现一个 `LLM` 类：它的 `__init__()` 方法加载分词器和模型权重；它的 `chat()` 方法根据用户输入，生成内容。Ray Serve 在此基础上添加了三个地方：

* 在类上添加 [`ray.serve.deployment`](https://docs.ray.io/en/latest/serve/api/doc/ray.serve.deployment_decorator.html) 装饰器，这个装饰器与 `ray.remote` 有些相似，表示该类是一个 `Deployment`。
* 定义一个 `async def __call__()` 方法，当用户的 HTTP 请求到达时会自动触发 `__call__()` 方法，`__call__()` 方法的参数是 `starlette.requests.Request`，也就是用户通过 HTTP 发送过来的请求。
* 通过 `chat = LLM.bind()` 生成这个 `Application`，`chat` 就是这个 `Application` 的入口。

```{code-block} python
:caption: llm.py
:name: code-llm
:emphasize-lines: 7,24-26,28

from transformers import AutoTokenizer, AutoModelForCausalLM
from starlette.requests import Request

import ray
from ray import serve

@serve.deployment(ray_actor_options={"num_cpus": 8, "num_gpus": 1})
class LLM:
    def __init__(self):
        self.model_dir = "AI-ModelScope/gemma-2b-it"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_dir,
            device_map="auto"
        )

    def chat(self, input_text: str) -> str:
        input_ids = self.tokenizer(input_text, return_tensors="pt").to("cuda")
        outputs = self.model.generate(**input_ids, max_new_tokens=1024)
        generated_text = self.tokenizer.decode(outputs[0])

        return generated_text
    
    async def __call__(self, http_request: Request) -> str:
        user_message: str = await http_request.json()
        return self.chat(user_message)

chat = LLM.bind()
```

将这段代码保存为 `llm.py`，接下来使用 Ray Serve 的命令行工具 `serve` 启动这个 `Application`：

```bash
serve run llm:chat
```

运行这段命令行前，我们必须确保当前工作目录下有 `llm.py` 这个文件，`llm:chat` 中的 `chat` 是 `llm.py` 文件中由 `chat = LLM.bind()` 方法生成的 `Application`。运行命令后，Ray Serve 会在 http://localhost:8000 提供该模型的推理服务。

### 客户端

上面定义的 `Application` 是一个简易的大语言模型推理服务，它提供了 HTTP 接口，但没有图形界面，无法使用浏览器打开，我们需要向服务端发送请求来访问这个推理服务，如 {numref}`code-client-chat` 所示。

```{code-block} python
:caption: client-chat.py
:name: code-client-chat

import requests

prompt = "Could you explain what is dask?"

response = requests.post("http://localhost:8000/", json=prompt)
print(response.text)
```

在命令行中执行这个客户端，它将语言模型生成的内容打印出来。

```bash
python client-chat.py
```

### 部署参数

`ray.serve.deployment` 有一些参数用来定义模型部署。Ray Serve 的模型运行在 Ray Actor 中，`ray_actor_options` 定义每个模型副本所需要的计算资源，尤其要注意，如果模型需要运行在 GPU 上，这里必须要定义 `{"num_gpus": n}`，否则 Ray 不会给这个任务分配 GPU。这里定义资源的方式与 {numref}`sec-ray-computing-resource` 中的方式是一致的。

`ray.serve.deployment` 另外一个重要的参数是 `num_replicas`，用来定义生成几个 `Deployment` 副本。

### 配置文件

除了在 `ray.serve.deployment` 编写代码定义外，也可以在配置文件中定义这些部署参数。配置文件是一个 YAML 文件，如 {numref}`code-config-yaml` 所示。

```{code-block} yaml
:caption: config.yaml
:name: code-config-yaml

proxy_location: EveryNode

http_options:
  host: 0.0.0.0
  port: 8901

grpc_options:
  port: 9000
  grpc_servicer_functions: []

applications:
- name: llm
  route_prefix: /
  import_path: llm:chat
  runtime_env: {}
  deployments:
  - name: LLM
    num_replicas: 1
    ray_actor_options:
      num_cpus: 8
      num_gpus: 1
```

比如在 `http_options` 下设置对外服务的 IP 地址（`host`）和端口号（`port`），Ray Serve 默认使用 `0.0.0.0` 和 `8000` 启动服务，`0.0.0.0` 使得该服务可公开访问。与 `http_options` 类似，`grpc_options` 是针对 gRPC 的。

`applications` 下是一个列表，可以定义多个 `Application`，每个 `Application` 需要定义 `import_path` 和 `route_prefix`。`import_path` 是这个 `Application` 的入口，`route_prefix` 对应 HTTP 服务的路由前缀。每个 `Application` 有一个或多个 `Deployments`，`Deployments` 的定义与 `ray.serve.deployment` 一致。

如果同时在配置文件和 `ray.serve.deployment` 都做了设置，Ray Serve 会优先使用配置文件中的参数设置。