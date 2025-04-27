import numpy as np
from os.path import join
import sys
import cupy as cp
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


def jacobi_gpu_cupy(u, interior_mask, max_iter=20000):
    u_device = cp.asarray(u)
    u_new_device = cp.copy(u_device)
    mask_device = cp.asarray(interior_mask)

    for _ in range(max_iter):
        # Only update the interior padded values (exclude boundary)
        u_new_device[:, 1:-1, 1:-1] = cp.where(
            mask_device,
            0.25 * (
                u_device[:, 2:, 1:-1] +
                u_device[:, :-2, 1:-1] + 
                u_device[:, 1:-1, 2:] +  
                u_device[:, 1:-1, :-2]   
            ),
            u_device[:, 1:-1, 1:-1]  
        )

        u_device, u_new_device = u_new_device, u_device

    return cp.asnumpy(u_device)


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
    u_final = jacobi_gpu_cupy(all_u0, all_interior_mask)

    # Print summary statistics in CSV format
    stat_keys = ['mean_temp', 'std_temp', 'pct_above_18', 'pct_below_15']
    print('building_id, ' + ', '.join(stat_keys))  # CSV header
    for bid, u, interior_mask in zip(building_ids, u_final, all_interior_mask):
        stats = summary_stats(u, interior_mask)
        print(f"{bid},", ", ".join(str(stats[k]) for k in stat_keys))
    
    # Plot
    plt_1(u_final, building_ids)