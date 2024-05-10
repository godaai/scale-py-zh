# Hierarchical Environment
from gymnasium.spaces import Discrete, Tuple
import logging
import os
import ray
from ray import air, tune
from ray.rllib.algorithms.ppo import PPOConfig
from windy_maze_env import WindyMazeEnv, HierarchicalWindyMazeEnv
from ray.rllib.utils.test_utils import check_learning_achieved

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
    # Use GPUs iff `RLLIB_NUM_GPUS` env var set to > 0.
    .resources(num_gpus=int(os.environ.get("RLLIB_NUM_GPUS", "0")))
)


results = tune.Tuner(
    "PPO",
    param_space=config.to_dict(),
    run_config=air.RunConfig(stop=stop, verbose=1),
).fit()