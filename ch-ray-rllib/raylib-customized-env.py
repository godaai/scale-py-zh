from ray.rllib.algorithms import ppo  #常见的算法有 BC,DQN,SAC,TD3,PPO等
import gymnasium as gym
import numpy as np
import math
from gymnasium import spaces, logger
from ray.tune.logger import pretty_print
from gymnasium.utils import seeding
import numpy as np

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

    # ####⑤render()源码
    # # render()函数在这里扮演图像引擎的角色。一个仿真环境必不可少的两部分是物理引擎和图像引擎。
    # # 物理引擎模拟环境中物体的运动规律；图像引擎用来显示环境中的物体图像
    # def render(self, mode='human'):
    #     screen_width = 600
    #     screen_heigt = 400  # 画布的高宽

    #     world_width = self.x_threshold * 2  # 整个小车在x轴的位置范围（2.4*2 = 4.8）
    #     scale = screen_width / world_width  # 尺寸600/4.8 =125
    #     carty = 100  # 小车离画布低端100
    #     polewidth = 10.0  # 杆的宽度
    #     polelen = scale * (2 * self.length)  # 125*（2*0.5）=125
    #     cartwidth = 50.0  # 小车宽度
    #     cartheight = 30.0  # 小车高读

    #     if self.viewer is None:  # 如果显示器是空的
    #         self.viewer = rendering.Viewer(screen_width, screen_heigt)  # 显示画布

    #         # 创建车
    #         l, r, t, b = -cartwidth / 2, cartwidth / 2, cartheight / 2, -cartheight / 2
    #         # l = -25, r = 25, t = 15, b = -15
    #         axleoffset = cartheight / 4.0  # 车轴7.5
    #         cart = rendering.FilledPolygon([(l, b), (l, t), (r, t), (r, b)])
    #         # 通过长方形的四个点来画小车，以小车的中心为原点，顺时针对应四个点的顺序（从第三象限为第一个点）
    #         # Transform给cart添加平移属性和旋转属性
    #         self.carttrans = rendering.Transform()
    #         cart.add_attr(self.carttrans)
    #         self.viewer.add_geom(cart)  # 在显示器上添加小车

    #         # 创建杆
    #         l, r, t, b = -polewidth / 2, polewidth / 2, polelen - polewidth / 2, -polewidth / 2
    #         # l = -5, r = 5, t =120，b=-5
    #         pole = rendering.FilledPolygon([(l, b), (l, t), (r, t), (r, b)])
    #         # 通过长方形的四个点来画杆，但是是以小车的中心为原点
    #         pole.set_color(.8, .6, .4)  # 给杆设置颜色
    #         # 添加摆杆装换矩阵属性
    #         self.poletrans = rendering.Transform(translation=(0, axleoffset))  # 杆中心平移（）
    #         pole.add_attr(self.poletrans)  # 对杆进行平移赋值
    #         pole.add_attr(self.carttrans)  # 对杆进行平移赋值
    #         self.viewer.add_geom(pole)  # 在显示器上添加杆

    #         # 创建摆杆和车之间的连接
    #         self.axle = rendering.make_circle(polewidth / 2)  # 圆的直径为5
    #         self.axle.add_attr(self.poletrans)  # 对圆进行平移赋值
    #         self.axle.add_attr(self.carttrans)  # 对圆进行平移赋值
    #         self.axle.set_color(.5, .5, .8)  # 给圆设置颜色
    #         self.viewer.add_geom(self.axle)  # 在显示器上添加圆

    #         # 创建轨道，即一条线
    #         self.track = rendering.Line((0, carty), (screen_width, carty))  # (0,100),(600,100)
    #         self.track.set_color(0, 0, 0)  # 给线设置颜色
    #         self.viewer.add_geom(self.track)  # 在显示器上添加线

    #         self._pole_geom = pole  # ???

    #     if self.state is None:
    #         return None

    #     # 编辑极点多边形顶点
    #     pole = self._pole_geom
    #     l, r, t, b = -polewidth / 2, polewidth / 2, polelen - polewidth / 2, -polewidth / 2
    #     # l = -5, r = 5, t = 120, b = -5
    #     pole.v = [(l, b), (l, t), (r, t), (r, b)]

    #     # 设置平移属性
    #     x = self.state #这里的x是状态，那么状态有四个属性，包括车位置x,车速x_dot, 杆角度theta, 杆顶端的速度theta_dot
    #     cartx = x[0] * scale + screen_width / 2.0  # 车中央  车位置 *125 +600/2
    #     self.carttrans.set_translation(cartx, carty)  # ？？？
    #     self.poletrans.set_rotation(-x[2])  # 杆角度的负数

    #     return self.viewer.render(return_rgb_array=mode == 'rgb_array')

    ####⑥
    def close(self):
        if self.viewer:
            self.viewer.close()
            self.viewer = None

# 自定义环境
myEnv=CartPoleEnv
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
