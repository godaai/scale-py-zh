# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 09:32:04 2024

@author: LY
"""

import matplotlib.pyplot as plt
import numpy as np

np.random.seed(3)

num_points = 1000
x = np.random.uniform(-1, 1, num_points)
y = np.random.uniform(-1, 1, num_points)
distance = np.sqrt(x**2 + y**2)
inside_circle = distance <= 1
num_inside_circle = np.sum(inside_circle)
pi_estimate = 4 * num_inside_circle / num_points

plt.figure(figsize=(7, 7))
plt.scatter(x, y, c=np.where(inside_circle, 'green', 'red'), alpha=0.7)
plt.axis('equal')
circle = plt.Circle((0, 0), 1, color='gray', fill=False)
plt.gca().add_artist(circle)
plt.axhline(y=-1, color='gray', linestyle='-')
plt.axhline(y=0, color='gray', linestyle='-')
plt.axhline(y=1, color='gray', linestyle='-')
plt.axvline(x=-1, color='gray', linestyle='-')
plt.axvline(x=0, color='gray', linestyle='-')
plt.axvline(x=1, color='gray', linestyle='-')
plt.xlim(-1.05, 1.05)
plt.ylim(-1.05, 1.05)
plt.xticks([-1,0,1], fontsize=12)
plt.yticks([-1,0,1], fontsize=12)
plt.title(f"1000 Samples\nPi~={pi_estimate:.3f}")
plt.savefig('D:\code\Github\distributed-python\img\ch-ray-core\square-circle.svg', format='svg')
plt.show()



