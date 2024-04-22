from transformers import AutoTokenizer, AutoModelForCausalLM
from starlette.requests import Request

import ray
from ray import serve

@serve.deployment(ray_actor_options={"num_cpus": 8, "num_gpus": 1})
class LLM:
    def __init__(self):
        # 将 `model_dir` 修改为您存放模型的地址
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