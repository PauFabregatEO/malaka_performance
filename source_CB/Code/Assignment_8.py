from os.path import join
import sys

import numpy as np
import matplotlib.pyplot as plt
from numba import cuda

TPB_X = 16  # Threads per block in X
TPB_Y = 16  # Threads per block in Y


def load_data(load_dir, bid):
    SIZE = 512
    u = np.zeros((SIZE + 2, SIZE + 2))
    u[1:-1, 1:-1] = np.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask = np.load(join(load_dir, f"{bid}_interior.npy"))
    return u, interior_mask


@cuda.jit
def jacobi_iteration_kernel(u, u_new, interior_mask):
    x, y = cuda.grid(2) #Computes the global (2D) thread index from block and thread indices.
    #Ensures that the current thread does not operate on the padded boundary
    if x >= 1 and x < u.shape[0] - 1 and y >= 1 and y < u.shape[1] - 1:
        if interior_mask[x - 1, y - 1]:  # interior_mask excludes the padding
            u_new[x, y] = 0.25 * (u[x-1, y] + u[x+1, y] + u[x, y-1] + u[x, y+1])
        else:
            u_new[x, y] = u[x, y]  # boundary or exterior points remain unchanged

def jacobi_cuda(u_host, interior_mask_host, max_iter):
    # Allocate device arrays
    u = cuda.to_device(u_host)
    u_new = cuda.device_array_like(u) #Allocates a GPU array of the same shape as u to store
    interior_mask = cuda.to_device(interior_mask_host) #Transfers the interior mask to GPU memory

    # Define block and grid dimensions
    threadsperblock = (TPB_X, TPB_Y) #Specifies the block size
    blockspergrid_x = (u.shape[0] + TPB_X - 1) // TPB_X
    blockspergrid_y = (u.shape[1] + TPB_Y - 1) // TPB_Y 
    blockspergrid = (blockspergrid_x, blockspergrid_y) #Calculates the number of blocks 

    for _ in range(max_iter):
        jacobi_iteration_kernel[blockspergrid, threadsperblock](u, u_new, interior_mask)
        u, u_new = u_new, u  # Swap references

    return u.copy_to_host()

def summary_stats(u, interior_mask):
    u_interior = u[1:-1, 1:-1][interior_mask]
    mean_temp = u_interior.mean()
    std_temp = u_interior.std()
    pct_above_18 = np.sum(u_interior > 18) / u_interior.size * 100
    pct_below_15 = np.sum(u_interior < 15) / u_interior.size * 100
    return {
        'mean_temp': mean_temp,
        'std_temp': std_temp,
        'pct_above_18': pct_above_18,
        'pct_below_15': pct_below_15,
    }


if __name__ == '__main__':
    # Load data
    LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'
    with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
        building_ids = f.read().splitlines()

    if len(sys.argv) < 2:
        N = 1
    else:
        N = int(sys.argv[1])
    building_ids = building_ids[:N]

    # Load floor plans
    all_u0 = np.empty((N, 514, 514))
    all_interior_mask = np.empty((N, 512, 512), dtype='bool')
    for i, bid in enumerate(building_ids):
        u0, interior_mask = load_data(LOAD_DIR, bid)
        all_u0[i] = u0
        all_interior_mask[i] = interior_mask

    # Run jacobi iterations for each floor plan
    MAX_ITER = 20_000
    ABS_TOL = 1e-4

    all_u = np.empty_like(all_u0)
    for i, (u0, interior_mask) in enumerate(zip(all_u0, all_interior_mask)):
        u = jacobi_cuda(u0, interior_mask, MAX_ITER)
        all_u[i] = u

    # Print summary statistics in CSV format
    stat_keys = ['mean_temp', 'std_temp', 'pct_above_18', 'pct_below_15']
    print('building_id, ' + ', '.join(stat_keys))  # CSV header
    for bid, u, interior_mask in zip(building_ids, all_u, all_interior_mask):
        stats = summary_stats(u, interior_mask)
        print(f"{bid},", ", ".join(str(stats[k]) for k in stat_keys))

        