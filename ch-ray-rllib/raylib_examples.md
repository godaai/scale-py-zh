# Example 1: RLlib一个简单的示例
通用的流程：(1)自定义/已有环境  (2)模型设计与实例化 (3)模型训练 (4)模型评估

```python
#常见的算法有 BC,DQN,SAC,TD3,PPO等
from ray.rllib.algorithms import ppo  
import gymnasium as gym
from cart-pole-env import CartPoleEnv

# 1.1 封装好的环境 Farama-Foundation Gymnasium environment: https://gymnasium.farama.org/content/basic_usage
myEnv="CartPole-v1"

# 1.2 自定义环境
myEnv=CartPoleEnv

# 2. 构建算法实例 (基于AlgorithmConfig类实现)
############参数解释:
# num_rollout_workers: 指定从环境中收集样本的并行workers的数量
#framework:可选项 torch, tf, tf2,
#training:模型训练配置，如gamma, lr, grad_clip, train_batch_size，optimizer等.
#evaluation: 算法评估配置,例如设定评估间隔、并行评估的worker数量等
############  

config = ppo.PPOConfig().environment(env=myEnv).rollouts(num_rollout_workers=3).framework("torch").training(model={"fcnet_hiddens": [64, 64]},lr=0.005,train_batch_size=3000).evaluation(evaluation_num_workers=1)

algo = config.build()

# 3. 训练算法
epoch=3
for _ in range(epoch):
    print(algo.train())

# 4.评估算法
algo.evaluate()
```


在命令行中这样启动：

```bash
python raylib-packaged-env.py
python raylib-customized-env.py
```

# Example 2: 切换不同的算法

RLlib已经提供了多种Off-policy和On-policy的算法

##Model-free Off-policy RL

(1) DQN实例化配置 (CartPole-v1环境为例)
```Python
from ray.rllib.algorithms.dqn.dqn import DQNConfig
from ray import air
from ray import tune
config = DQNConfig().framework('torch').training( 
    num_atoms=tune.grid_search(list(range(1,6))))
    .environment(env="CartPole-v1") 
#  trainable=> 要被调优的trainer
#  param_space=>参数搜索空间
#  run_config=>运行时配置设定，如果通过，则传递给trainer
tune.Tuner(  
    trainable="DQN",
    run_config=air.RunConfig(stop={"episode_reward_mean":200}),
    param_space=config.to_dict()
).fit()
```

(2) SAC实例化配置
```Python
sac_config = SACConfig().training(gamma=0.9, lr=0.01).resources(num_gpus=0).rollouts(num_rollout_workers=4)    
algo = sac_config.build(env="CartPole-v1")  
algo.train()  
```

##Model-free Off-policy RL

(3) BC实例化配置 (BC试图匹配生成离线数据的行为策略)
```Python
from ray.rllib.algorithms.bc import BCConfig
config = BCConfig().training(lr=0.00001, gamma=0.99).offline_data(input_="./rllib/tests/data/cartpole/large.json")
config.build().train()  
```

(4) MARWIL实例化配置
```Python
from ray.rllib.algorithms.marwil import MARWILConfig
from ray import tune
config = MARWILConfig().training(lr=tune.grid_search(  
    [0.001, 0.0001]), beta=0.75)
# 设置配置对象的数据路径
config.offline_data( 
    input_=["./rllib/tests/data/cartpole/large.json"])
# 设置配置对象的环境
config.environment(env="CartPole-v1")  
# 训练并调优配置参数
tune.Tuner(  
    "MARWIL",
    param_space=config.to_dict(),
).fit()
```


# Example 3: 多智能体环境

在某些环境中(例如棋牌类游戏、交通系统等)，需要设置多个智能体同时施加动作或者按次序交互的方式。

首先建立multi-agent算法配置：
```Python
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

def gen_policy(i):
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

##################
#policies: 字典对象{policy id-> Policy config}
#policy_mapping_fn: 映射函数(agent id-> policy id)
#policies_to_train: 需要被更新的策略 
##################
config = (
    PPOConfig()
    .environment(MultiAgentCartPole, env_config={"num_agents": num_agents})
    .framework("torch")
    .training(num_sgd_iter=10)
    .multi_agent(policies=policies, policy_mapping_fn=policy_mapping_fn)
    .resources(num_gpus=0)
)
```

然后实例化算法，并手动设置训练过程：
```Python
algo=config.build()
epoch=15
for _ in range(epoch):
    results=algo.train()
    print(pretty_print(results))
```
在命令行中启动：

```bash
python multi-agent-train.py
```


或者利用ray.tune设置自动化训练过程，并优化超参数：

```Python
stop_reward=150.0
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
# 验证是否达到预期结果
check_learning_achieved(results, stop_reward)
```

在命令行中启动：

```bash
python multi-agent-tune.py
```

# Example 4: 层次(Hierarchical)环境

在某些场景下，为完成特定任务，需要采取层次化的决策。在每一轮行动中，首先在`level 1`进行决策$a_1$, 然后根据$a_1$在`level 2`进行决策$a_2$，...直到`level n`实施$a_n$完成，此后循环往复，到完成任务为止。

```Python
from gymnasium.spaces import Discrete, Tuple
import logging
import os
import ray
from ray import air, tune
from ray.rllib.algorithms.ppo import PPOConfig
from windy_maze_env import WindyMazeEnv, HierarchicalWindyMazeEnv
from ray.rllib.utils.test_utils import check_learning_achieved

# 环境WindyMaze：从迷宫的起点位置 S 抵达终点位置 F。该环境分为两层决策，高层 action 目的是设置一个临时的目标位置，低层 action 为在东西南北四个方向移动一步。若到达临时目标位置，将获得更高奖励。
maze = WindyMazeEnv(None)

def policy_mapping_fn(agent_id, episode, worker, **kwargs):
    if agent_id.startswith("low_level_"):
        return "low_level_policy"
    else:
        return "high_level_policy"

stop = {
        "training_iteration": 200,
        "timesteps_total": 100000,
        "episode_reward_mean": 0.0,
    }

config = (
    PPOConfig()
    .environment(HierarchicalWindyMazeEnv)
    .framework("torch")
    .rollouts(num_rollout_workers=0)
    .training(entropy_coeff=0.01)
    .multi_agent(
        policies={
            "high_level_policy": (
                None,
                maze.observation_space,
                Discrete(4),
                PPOConfig.overrides(gamma=0.9),
            ),
            "low_level_policy": (
                None,
                Tuple([maze.observation_space, Discrete(4)]),
                maze.action_space,
                PPOConfig.overrides(gamma=0.0),
            ),
        },
        policy_mapping_fn=policy_mapping_fn,
    )
    .resources(num_gpus=int(os.environ.get("RLLIB_NUM_GPUS", "0")))
)

results = tune.Tuner(
    "PPO",
    param_space=config.to_dict(),
    run_config=air.RunConfig(stop=stop, verbose=1),
).fit()
```

在命令行中启动：

```bash
python hierarchical-agent-tune.py
```

# Example 5: RLlib CLI训练模型

Acrobot系统环境由两个线性连接的链组成，其中一个链的一端固定，另一个链的自由端配有驱动关节。目标是在从下垂的初始状态开始时，通过对驱动关节施加扭矩，使线性链的自由端摆动到给定高度。

在命令行中，直接执行RL训练任务(参数可按需调整)即可：

```bash
rllib train --algo SAC --env Acrobot-v1 --stop '{"training_iteration": 50}'
```

