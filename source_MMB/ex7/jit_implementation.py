from os.path import join
import sys
from numba import njit
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


@njit(cache=True)
def jacobi_jit(u, interior_mask, max_iter, atol=1e-6):
    u = u.copy()
    SIZE = u.shape[0] - 2
    u_new = np.empty_like(u)
    delta =np.empty((512, 512), dtype=np.float32)

    for it in range(max_iter):
        # i outer so better cache wise
        for i in range(1, SIZE + 1):
            # j inner to avoid cache misses as indexing is done column-wise
            for j in range(1, SIZE + 1):
                # Check if cell is inside the mask
                if interior_mask[i - 1, j - 1]:
                    val = 0.25 * (u[i+1, j] + u[i-1, j] + u[i, j+1] + u[i, j-1])
                    delta[i - 1, j - 1] = abs(u[i, j] - val)
                    u_new[i, j] = val
                else:
                    u_new[i, j] = u[i, j] 

        if np.max(delta) < atol:
            break

        u = u_new 
    return u



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
        u = jacobi_jit(u0, interior_mask, MAX_ITER, ABS_TOL)
        all_u[i] = u

    jacobi_jit.inspect_types() # will show JIT types and confirm compilation

    # Print summary statistics in CSV format
    stat_keys = ['mean_temp', 'std_temp', 'pct_above_18', 'pct_below_15']
    print('building_id, ' + ', '.join(stat_keys))  # CSV header
    for bid, u, interior_mask in zip(building_ids, all_u, all_interior_mask):
        stats = summary_stats(u, interior_mask)
        print(f"{bid},", ", ".join(str(stats[k]) for k in stat_keys))

    # Plot 
    plt_1(all_u, building_ids)