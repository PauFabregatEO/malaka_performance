#!/usr/bin/python
from os.path import join
import sys
import numpy as np
import multiprocessing
from plot import plot_u


def load_data(load_dir, bid):
    SIZE = 512
    u = np.zeros((SIZE + 2, SIZE + 2))
    u[1:-1, 1:-1] = np.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask = np.load(join(load_dir, f"{bid}_interior.npy"))
    return u, interior_mask

def jacobi(u, interior_mask, max_iter=20000, atol=1e-6):
    u = np.copy(u)
    
    for i in range(max_iter):
        # Compute average of left, right, up and down neighbors, see eq. (1)
        u_new = 0.25 * (u[1:-1, :-2] + u[1:-1, 2:] + u[:-2, 1:-1] + u[2:, 1:-1])
        u_new_interior = u_new[interior_mask]
        delta = np.abs(u[1:-1, 1:-1][interior_mask] - u_new_interior).max()
        u[1:-1, 1:-1][interior_mask] = u_new_interior

        if delta < atol:
            break
    return u

def jacobi_multiple(chunk_building_ids, load_dir, max_iter=20000, atol=1e-6):
    results = {}
    for bid in chunk_building_ids:
        u0, interior_mask = load_data(load_dir, bid)
        u = jacobi(u0, interior_mask, max_iter, atol)
        results[bid] = (u, interior_mask)
    return results

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
        n_proc = 1
    else:
        N = int(sys.argv[1])
        n_proc = int(sys.argv[2])
    building_ids = building_ids[:N]

    # Run jacobi iterations for each floor plan
    MAX_ITER = 20_000
    ABS_TOL = 1e-4
    chunk_size = N / n_proc

    # Define parallelization parameters
    pool = multiprocessing.Pool(n_proc)
    results_async = [pool.apply_async(jacobi_multiple, (chunk_building_ids, LOAD_DIR)) 
                     for chunk_building_ids in np.array_split(building_ids,int(chunk_size))]
        
    all_results = {bid: res for result in results_async for bid, res in result.get().items()}
    
    #print('building_id, mean_temp, std_temp, pct_above_18, pct_below_15')
    for bid, (u, interior_mask) in all_results.items():
        stats = summary_stats(u, interior_mask)
        print(f"{bid}, {stats['mean_temp']}, {stats['std_temp']}, {stats['pct_above_18']}, {stats['pct_below_15']}")

    
    ''' Already checked outputs make sense
    for u, id in zip(all_u0, building_ids):
        plot_u(u, id, '_n{}'.format(n_proc))
    ''' 