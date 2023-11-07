from mpi4py import MPI
import numpy as np

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

sendbuf = None
if rank == 0:
    sendbuf = np.empty([size, 8], dtype='i')
    sendbuf.T[:,:] = range(size)
    print(f"Rank: {rank}, to be scattered: \n{sendbuf}")
recvbuf = np.empty(8, dtype='i')
comm.Scatter(sendbuf, recvbuf, root=0)
print(f"Rank: {rank}, after scatter: {recvbuf}")
assert np.allclose(recvbuf, rank)