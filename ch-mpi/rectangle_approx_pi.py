from mpi4py import MPI
import time
import math
communicator=MPI.COMM_WORLD
rank=communicator.Get_rank()  #进程唯一的标识Rank
process_nums=communicator.Get_size()
"""
参数设置：
R=1
N=64*1024*1024
"""
t0=time.time()
rect_num=64 * 1024 * 1024
rect_width=1/rect_num
step_size=rect_num//process_nums

def cal_rect_area(process_no,step_size,rect_width):
    tot_area=0.0
    rect_start=(process_no*step_size+1)*rect_width

    for i in range(step_size):
        x=rect_start+i*rect_width
        #  (x,y) 对应于第i个小矩形唯一在圆弧上的顶点，容易知道x^2+y^2=1  ==> y=sqrt(1-x^2)
        rect_length=math.pow(1-x*x, 0.5)
        tot_area+=rect_width*rect_length
    return tot_area


tot_area=cal_rect_area(rank,step_size,rect_width)
#设置master rank为0，worker rank为其它
if rank==0:
    for i in range(1,process_nums):
        tot_area+=communicator.recv(source=i)
    p_i=tot_area * 4
    t1=time.time()
    print('模拟PI值为: {:.10f}, 相对误差为：{:.10f}'.format(p_i,abs(1-p_i/math.pi))) 
    print('并行耗时：{:.3f}s'.format(t1 - t0))
    # 串行执行
    t2=time.time()
    tot_area=cal_rect_area(rank,rect_num,rect_width)
    # print(4*tot_area)
    t3=time.time()
    print('串行耗时：{:.3f}s'.format(t3 - t2))

else:
    communicator.send(tot_area,dest=0)