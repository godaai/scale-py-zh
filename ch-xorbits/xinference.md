(sec-xinference)=
# Xinference

Xorbits Inference (Xinference) 是一款面向大模型的推理平台，支持大语言模型、向量模型、文生图模型等。它底层基于 [Xoscar](https://github.com/xorbitsai/xoscar) 提供的分布式能力，使得模型可以在集群上部署，上层提供了类 OpenAI 的接口，用户可以在上面部署和调用开源大模型。Xinference 将对外服务的 API、推理引擎和硬件做了集成，不需要像 Ray Serve 编写代码来管理模型推理服务。

## 推理引擎

Xinference 可适配不同推理引擎，包括 Hugging Face Transformers、[vLLM](https://github.com/vllm-project/vllm)、[llama.cpp](https://github.com/ggerganov/llama.cpp) 等，因此在安装时也要安装对应的推理引擎，比如 `pip install "xinference[transformers]"`。Transformers 完全基于 PyTorch，适配的模型最快最全，但性能较差；其他推理引擎，比如 vLLM、llama.cpp 专注于性能优化，但模型覆盖度没 Transformers 高。

## 集群

使用之前需要先启动一个 Xinference 推理集群，可以是单机多卡，也可以是多机多卡。单机上可以在命令行里这样启动：

```shell
xinference-local --host 0.0.0.0 --port 9997
```

集群场景与 Xorbits Data 类似，先启动一个 Supervisor，再启动 Worker：

```shell
# 启动 Supervisor
xinference-supervisor -H <supervisor_ip>

# 启动 Worker
xinference-worker -e "http://<supervisor_ip>:9997" -H <worker_ip>
```

之后就可以在 http://<supervisor_ip>:9997 访问 Xinference 服务。

## 使用模型

Xinference 可以管理模型部署的整个生命周期：启动模型、使用模型、关闭模型。

启动 Xinference 服务后，我们就可以启动模型并调用模型，Xinference 集成了大量开源模型，用户可以在网页中选择一个启动，Xinference 会在后台下载并启动这个模型。每个启动的模型既有网页版对话界面，又兼容 OpenAI 的 API。比如，使用 OpenAI 的 API 与某个模型交互：

```
from openai import OpenAI
client = OpenAI(base_url="http://127.0.0.1:9997/v1", api_key="not used actually")

response = client.chat.completions.create(
    model="my-llama-2",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the largest animal?"}
    ]
)
print(response)
```