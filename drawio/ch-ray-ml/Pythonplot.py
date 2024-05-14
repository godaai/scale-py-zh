# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 18:49:12 2024

@author: LY
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

harvest = np.array([[2.8, 2.4, 2.6, 3.0, 3.2, 3.5, 3.2],
                    [2.4, 2.3, 2.1, 2.5, 3.4, 6.0, 3.5],
                    [3.1, 2.0, 0.1, 0.3, 3.2, 3.4, 2.8],
                    [4.6, 2.5, 0.3, 1.2, 1.8, 1.6, 1.8],
                    [6.0, 5.6, 2.6, 1.8, 0.1, 0.3, 0.8],
                    [5.5, 4.5, 3.5, 1.5, 0.3, 0.0, 0.6],
                    [4.5, 4.0, 3.0, 2.4, 0.8, 0.5, 0.2]])

# https://plotly.com/python/builtin-colorscales/

fig, ax = plt.subplots(figsize=(4, 4))
im = ax.imshow(harvest,interpolation="gaussian",cmap='jet')
ax.axis('off')
rect = patches.Rectangle((-0.5, -0.5), harvest.shape[1], harvest.shape[0], linewidth=2, edgecolor='black', facecolor='none')
ax.add_patch(rect)

fig.savefig(r'./figure.svg', format="svg")
