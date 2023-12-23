import math
import time

from mpi4py import MPI

communicator = MPI.COMM_WORLD
rank = communicator.Get_rank()  # 进程唯一的标识Rank
process_nums = communicator.Get_size()
"""
参数设置：
R=1
N=64*1024*1024
"""
t0 = time.time()
rect_num = 64 * 1024 * 1024
rect_width = 1 / rect_num
step_size = rect_num // process_nums

def cal_rect_area(process_no, step_size, rect_width):
    total_area = 0.0
    rect_start = (process_no * step_size + 1) * rect_width

    for i in range(step_size):
        x = rect_start + i * rect_width
        # (x,y) 对应于第i个小矩形唯一在圆弧上的顶点
        # x^2+y^2=1 => y=sqrt(1-x^2)
        rect_length = math.pow(1 - x * x, 0.5)
        total_area += rect_width * rect_length
    return total_area

# 在每个进程上执行计算
total_area = cal_rect_area(rank, step_size, rect_width)

if rank == 0:
    # Master
    for i in range(1, process_nums):
        total_area += communicator.recv(source=i)
    p_i = total_area * 4
    t1 = time.time()
    print("Simulated PI: {:.10f}, Relative Error：{:.10f}".format(p_i, abs(1 - p_i / math.pi)))
    print("Time：{:.3f}s".format(t1 - t0))
else:
    # Worker
    communicator.send(total_area, dest=0)