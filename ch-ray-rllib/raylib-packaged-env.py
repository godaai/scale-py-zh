from ray.rllib.algorithms import ppo  #常见的算法有 BC,DQN,SAC,TD3,PPO等
from ray.tune.logger import pretty_print

# 封装好的环境 Farama-Foundation Gymnasium environment: https://gymnasium.farama.org/content/basic_usage
myEnv="CartPole-v1"

# num_rollout_workers:  specify the number of parallel workers to collect samples from the environment.
config = ppo.PPOConfig().environment(env=myEnv).rollouts(num_rollout_workers=3).framework("torch").training(model={"fcnet_hiddens": [64, 64]},train_batch_size=3000).evaluation(evaluation_num_workers=1)


# 2. 构建算法实例
algo = config.build()

# 3. 训练算法
epoch=3
for _ in range(epoch):
    print(pretty_print(algo.train()))

# 4.评估算法
algo.evaluate()
