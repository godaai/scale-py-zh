import gymnasium as gym
import numpy as np
import math
from gymnasium import spaces, logger
from gymnasium.utils import seeding
# custom环境,  继承 Gymnasium.Env类, 实现 step, reset, render, colse
# 构建器函数必须只接收env_config单个参数
class CartPoleEnv(gym.Env):
    metadata = {
        'render.modes': ['human', 'rgb_array'],
        'video.frames_per_second': 50
    }
    #####①
    def __init__(self,env_config):
        self.gravity = 9.8 #重力加速度g
        self.masscart = 1.0 #车重量
        self.masspole = 0.1 #杆重量
        self.total_mass = (self.masspole + self.masscart) #（0.1 + 1） = 1.1，车和杆的重量
        self.length = 0.5  # 计算杆高度用
        self.polemass_length = (self.masspole * self.length) #（0.1 * 0.5） = 0.05，计算加速度用
        self.force_mag = 10.0 #输入动作，每次施加给车的力
        self.tau = 0.02  # 状态state更新之间的秒数
        self.kinematics_integrator = 'euler' #运动学积分器，为了计算下一步state

        # Angle at which to fail the episode 本局失败的角度
        self.theta_threshold_radians = 12 * 2 * math.pi / 360  # 12 * 2 * 180° / 360° = 12 °
        self.x_threshold = 2.4

        # Angle limit set to 2 * theta_threshold_radians so failing observation
        # 角度限制设为 2 * theta_threshold_radians，这就是失败的观察

        # is still within bounds. 仍在范围内
        high = np.array([self.x_threshold * 2, # 4.8
                         np.finfo(np.float32).max, #取float的最大值
                         self.theta_threshold_radians * 2, #24°
                         np.finfo(np.float32).max], #取float的最大值
                        dtype=np.float32)

        self.action_space = spaces.Discrete(2) #离散动作定义（2个动作）为0,1

        self.observation_space = spaces.Box(-high, high, dtype=np.float32) #连续状态定义(四种都是连续的)
        # Num     Observation               Min                     Max
        # 0       Cart Position             -4.8                    4.8
        # 1       Cart Velocity             -Inf                    Inf
        # 2       Pole Angle                -0.418 rad (-24 deg)    0.418 rad (24 deg)
        # 3       Pole Angular Velocity     -Inf                    Inf

        self.seed()
        self.viewer = None
        self.state = None
        self.steps_beyond_done = None

    ####②
    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    ###③step()源码
    # 该函数在仿真器中扮演物理引擎的角色，。一个仿真环境必不可少的两部分是物理引擎和图像引擎。
    # 物理引擎模拟环境中物体的运动规律；图像引擎用来显示环境中的物体图像
    # 该函数描述了智能体与环境交互的所有信息。 输入：action，输出：observation，reward，done，info
    def step(self, action):
        err_msg = "%r (%s) invalid" % (action, type(action))
        assert self.action_space.contains(action), err_msg  # 判断动作空间是否包含输入的action，否则报err_msg的错

        x, x_dot, theta, theta_dot = self.state  # 系统当前状态，包括车位置x,车速x_dot, 杆角度theta, 杆顶端的速度theta_dot
        force = self.force_mag if action == 1 else -self.force_mag  # 输入动作，（1代表右），即作用到车上的力
        costheta = math.cos(theta)  # 计算角度cos值
        sintheta = math.sin(theta)  # 计算角度sin值

        # 施加力对杆子和小车影响的数学公式
        # temp:车摆的动力学方程式，即加速度与动作之间的关系
        temp = (force + self.polemass_length * theta_dot ** 2 * sintheta) / self.total_mass
        # temp=(±10 + 0.05 * 杆顶速度^2 * sin() ) / 1.1
        # thetaacc:摆的角加速度
        thetaacc = (self.gravity * sintheta - costheta * temp) / (
                self.length * (4.0 / 3.0 - self.masspole * costheta ** 2 / self.total_mass))
        # 小车的平加速度
        xacc = temp - self.polemass_length * thetaacc * costheta / self.total_mass

        # 计算下一步的state（x, x_dot, theta, theta_dot）
        if self.kinematics_integrator == 'euler':  # （欧拉）
            # tau是更新步长0.02
            x = x + self.tau * x_dot
            x_dot = x_dot + self.tau * xacc
            theta = theta + self.tau * theta_dot
            theta_dot = theta_dot + self.tau * thetaacc
        else:  # 半隐式欧拉
            x_dot = x_dot + self.tau * xacc
            x = x + self.tau * x_dot
            theta_dot = theta_dot + self.tau * thetaacc
            theta = theta + self.tau * theta_dot

        self.state = (x, x_dot, theta, theta_dot)
        # state包括车位置x,车速x_dot, 杆角度theta, 杆顶端的速度theta_dot

        # 结束的条件
        done = bool(
            x < -self.x_threshold
            or x > self.x_threshold  # 车的位置小于-2.4，大于2.4
            or theta < -self.theta_threshold_radians
            or theta > self.theta_threshold_radians  # 角度小于-12°，大于12°
        )

        # 奖励
        if not done:
            reward = 1.0
        elif self.steps_beyond_done is None:
            # Pole just fell! 杆刚落下
            self.steps_beyond_done = 0
            reward = 1.0
        else:
            if self.steps_beyond_done == 0:
                logger.warn("您正在调用‘step（）’，即使此环境已返回done=True。"
                            "一旦收到‘done=True’，您应该始终调用‘reset（）’——任何进一步的步骤都是未定义的行为。")

            self.steps_beyond_done += 1  # 当前的step加一
            reward = 0.0  # 奖励为0

        return np.array(self.state), reward, done, {}

    ####④reset()源码，self.np_random从 def seed()来
    def reset(self):
        # 初始化环境状态，所有观察值都被赋予（-0.05，0.05）中一个均匀随机值
        self.state = self.np_random.uniform(low=-0.05, high=0.05, size=(4,))
        # 从一个均匀分布[low,high)中随机采样，注意定义域是左闭右开，

        # 设置当前步数为None
        self.steps_beyond_done = None

        # 返回环境的初始化状态
        return np.array(self.state)

    ####⑥
    def close(self):
        if self.viewer:
            self.viewer.close()
            self.viewer = None