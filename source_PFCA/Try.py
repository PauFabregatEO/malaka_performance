#!/usr/bin/python
import multiprocessing
from os.path import join
import sys
import numpy as np

def load_data(load_dir, bid):
    SIZE = 512
    u = np.zeros((SIZE + 2, SIZE + 2))
    u[1:-1, 1:-1] = np.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask = np.load(join(load_dir, f"{bid}_interior.npy"))
    return u, interior_mask

def jacobi(u, interior_mask, max_iter, atol=1e-6):
    u = np.copy(u)
    for _ in range(max_iter):
        u_new = 0.25 * (u[1:-1, :-2] + u[1:-1, 2:] + u[:-2, 1:-1] + u[2:, 1:-1])
        u_new_interior = u_new[interior_mask]
        delta = np.abs(u[1:-1, 1:-1][interior_mask] - u_new_interior).max()
        u[1:-1, 1:-1][interior_mask] = u_new_interior
        if delta < atol:
            break
    return u

def process_floorplans(building_ids, load_dir, max_iter, atol):
    results = {}
    for bid in building_ids:
        u0, interior_mask = load_data(load_dir, bid)
        u = jacobi(u0, interior_mask, max_iter, atol)
        results[bid] = (u, interior_mask)
    return results

def summary_stats(u, interior_mask):
    u_interior = u[1:-1, 1:-1][interior_mask]
    return {
        'mean_temp': u_interior.mean(),
        'std_temp': u_interior.std(),
        'pct_above_18': np.sum(u_interior > 18) / u_interior.size * 100,
        'pct_below_15': np.sum(u_interior < 15) / u_interior.size * 100,
    }

if __name__ == '__main__':
    LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'
    with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
        building_ids = f.read().splitlines()

    N = int(sys.argv[1]) 
    building_ids = building_ids[:N]
    
    MAX_ITER = 20_000
    ABS_TOL = 1e-4
    n_proc = int(sys.argv[2])
    chunk_size = max(1, len(building_ids) // n_proc)
    
    with multiprocessing.Pool(n_proc) as pool:
        chunks = [building_ids[i:i + chunk_size] for i in range(0, len(building_ids), chunk_size)]
        results_list = pool.starmap(process_floorplans, [(chunk, LOAD_DIR, MAX_ITER, ABS_TOL) for chunk in chunks])
    
    all_results = {bid: res for result in results_list for bid, res in result.items()}
    
    #print('building_id, mean_temp, std_temp, pct_above_18, pct_below_15')
    for bid, (u, interior_mask) in all_results.items():
        stats = summary_stats(u, interior_mask)
        print(f"{bid}, {stats['mean_temp']}, {stats['std_temp']}, {stats['pct_above_18']}, {stats['pct_below_15']}")
