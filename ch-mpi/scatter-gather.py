import numpy as np
from mpi4py import MPI

comm = MPI.COMM_WORLD

my_N = 4
N = my_N * comm.size

if comm.rank == 0:
    A = np.arange(N, dtype=np.float64)
else:
    A = np.empty(N, dtype=np.float64)

my_A = np.empty(my_N, dtype=np.float64)

# Scatter data into my_A arrays
comm.Scatter([A, MPI.DOUBLE], [my_A, MPI.DOUBLE])

if comm.rank == 0:
    print("After Scatter:")
for r in range(comm.size):
    if comm.rank == r:
        print("Rank: %d, data: %s" % (comm.rank, my_A))
comm.Barrier()

# Everybody is multiplying by 2
# my_A *= 2

# # Allgather data into A again
# comm.Allgather([my_A, MPI.DOUBLE], [A, MPI.DOUBLE])

# if comm.rank == 0:
#     print("After Allgather:")
# for r in range(comm.size):
#     if comm.rank == r:
#         print("Rank%d, data:%s" % (comm.rank, A))
# comm.Barrier()