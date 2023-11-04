from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

if rank == 0:
    data = {'a': 7, 'b': 3.14}
    req = comm.isend(data, dest=1, tag=11)
    print(f"Sending: {data}, from rank: {rank}.")
    req.wait()
    print(f"Sended: {data}, from rank: {rank}.")
elif rank == 1:
    req = comm.irecv(source=0, tag=11)
    print(f"Receiving: to rank: {rank}.")
    data = req.wait()
    print(f"Received: {data}, to rank: {rank}.")