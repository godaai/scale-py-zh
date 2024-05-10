# 多个智能体环境 (version 1)
import os
import random
from ray import air, tune
from ray.rllib.algorithms.ppo import PPOConfig
from ray.rllib.examples.env.multi_agent import MultiAgentCartPole
from ray.rllib.examples.models.shared_weights_model import TorchSharedWeightsModel
from ray.rllib.models import ModelCatalog
from ray.rllib.policy.policy import PolicySpec
from ray.rllib.utils.framework import try_import_tf
from ray.rllib.utils.test_utils import check_learning_achieved

mod1 = mod2 = TorchSharedWeightsModel
ModelCatalog.register_custom_model("model1", mod1)
ModelCatalog.register_custom_model("model2", mod2)
num_policies=2
num_agents=4
stop_reward=150.0
def gen_policy(i):
    if bool(os.environ.get("RLLIB_ENABLE_RL_MODULE", False)):
        # just change the gammas between the two policies.
        # changing the module is not a critical part of this example.
        # the important part is that the policies are different.
        config = {
            "gamma": random.choice([0.95, 0.99]),
        }
    else:
        config = PPOConfig.overrides(
            model={
                "custom_model": ["model1", "model2"][i % 2],
            },
            gamma=random.choice([0.95, 0.99]),
        )
    return PolicySpec(config=config)
policies = {"policy_{}".format(i): gen_policy(i) for i in range(num_policies)}
policy_ids = list(policies.keys())

def policy_mapping_fn(agent_id, episode, worker, **kwargs):
    pol_id = random.choice(policy_ids)
    return pol_id

config = (
    PPOConfig()
    .environment(MultiAgentCartPole, env_config={"num_agents": num_agents})
    .framework("torch")
    .training(num_sgd_iter=10)
    .multi_agent(policies=policies, policy_mapping_fn=policy_mapping_fn)
    # Use GPUs iff `RLLIB_NUM_GPUS` env var set to > 0.
    .resources(num_gpus=int(os.environ.get("RLLIB_NUM_GPUS", "0")))
)

# 利用ray.tune自动训练，设置调优过程。
stop = {
    "episode_reward_mean": stop_reward,
    "timesteps_total": 100000,
    "training_iteration": 200,
}

results = tune.Tuner(
    "PPO",
    param_space=config.to_dict(),
    run_config=air.RunConfig(stop=stop, verbose=1),
).fit()

check_learning_achieved(results, stop_reward)  # 测试是否达到预期结果