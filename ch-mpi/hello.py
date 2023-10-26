from mpi4py import MPI

comm = MPI.COMM_WORLD

print(f"Hello! I'm rank {comm.Get_rank()} of {comm.Get_size()} running on host {MPI.Get_processor_name()}.")

comm.Barrier()