from numba import cuda
import numpy as np
from os.path import join
import sys
import numpy as np
from plot import plt_1

# import debugpy

# debugpy.listen(('0.0.0.0', 5677))
# print('Wait for debugger...')
# debugpy.wait_for_client()
# print('Connected!')

def load_data(load_dir, bid):
    SIZE = 512
    u = np.zeros((SIZE + 2, SIZE + 2))
    u[1:-1, 1:-1] = np.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask = np.load(join(load_dir, f"{bid}_interior.npy"))
    return u, interior_mask


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

@cuda.jit
def jacobi_kernel(u, u_new, mask):

    i = cuda.blockIdx.x * cuda.blockDim.x + cuda.threadIdx.x + 1
    j = cuda.blockIdx.y * cuda.blockDim.y + cuda.threadIdx.y + 1
    z = cuda.blockIdx.z

    if (1 <= i < u.shape[1] - 1) and (1 <= j < u.shape[2] - 1):
        if mask[z, i - 1, j - 1]:
            new_val = 0.25 * (u[z, i+1, j] + u[z, i-1, j] + u[z, i, j+1] + u[z, i, j-1])
            u_new[z, i, j] = new_val

def jacobi_gpu(u, interior_mask, max_iter=7000):

    # Send everything to memory in the GPU

    u_device = cuda.to_device(u)
    u_new_device = cuda.to_device(u)
    mask_device = cuda.to_device(interior_mask)

    TPB_X = 16
    TPB_Y = 16

    threadsperblock = (TPB_X, TPB_Y, 1)
    # Shape given by 514 - 2, dont initialize threads for points outside the grid
    blockspergrid_x = (u.shape[1] - 2 + TPB_X - 1) // TPB_X
    blockspergrid_y = (u.shape[2] - 2 + TPB_Y - 1) // TPB_Y
    blockspergrid_z = u.shape[0]

    blockspergrid = (blockspergrid_x, blockspergrid_y, blockspergrid_z)


    for _ in range(max_iter):
        # Uncheck when debugging is done
        jacobi_kernel[blockspergrid, threadsperblock](u_device, u_new_device, mask_device)
        # jacobi_kernel[2, 1](u_device, u_new_device, mask_device) 
        cuda.synchronize()
        # Swap u and u_new
        u_device, u_new_device = u_new_device, u_device

    return u_device.copy_to_host()

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

    # GPU part
    u_final = jacobi_gpu(all_u0, all_interior_mask)

    # Print summary statistics in CSV format
    stat_keys = ['mean_temp', 'std_temp', 'pct_above_18', 'pct_below_15']
    print('building_id, ' + ', '.join(stat_keys))  # CSV header
    for bid, u, interior_mask in zip(building_ids, u_final, all_interior_mask):
        stats = summary_stats(u, interior_mask)
        print(f"{bid},", ", ".join(str(stats[k]) for k in stat_keys))
    
    # Plot
    plt_1(u_final, building_ids)