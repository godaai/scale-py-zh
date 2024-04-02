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