#!/usr/bin/python
import multiprocessing
from os.path import join
import sys
import numpy as np
import time

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

def process_floorplans(u, interior_mask, load_dir, max_iter, atol):
    results = []
    for u0, im0 in zip(u,interior_mask):
        u = jacobi(u0, im0, max_iter, atol)
        results.append(u)
    return np.array(results)

def summary_stats(u, interior_mask):
    u_interior = u[1:-1, 1:-1][interior_mask]
    return {
        'mean_temp': u_interior.mean(),
        'std_temp': u_interior.std(),
        'pct_above_18': np.sum(u_interior > 18) / u_interior.size * 100,
        'pct_below_15': np.sum(u_interior < 15) / u_interior.size * 100,
    }

def split_array(array, size):
    result = []
    for i in range(0, len(array), size):
        result.append(array[i:i+size])
    return result

if __name__ == '__main__':
    LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'
    with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
        building_ids = f.read().splitlines()
    
    # Handle argument 1: Number of floorplans
    N = int(sys.argv[1]) 
    if len(sys.argv) < 2:
        N = 1
    else:
        N = int(sys.argv[1])
    building_ids = building_ids[:N]

    # Handle argument 2: Number of processors
    if len(sys.argv) < 3:
        n_proc = 1
    else:
        n_proc = int(sys.argv[2])
    
    # Handle argument 4: Chunksize
    if len(sys.argv) < 4:
        chunk_size = N / n_proc
    else:
        chunk_size = int(sys.argv[3])
        
    MAX_ITER = 20_000
    ABS_TOL = 1e-4
    
    # Load floor plans
    all_u0 = np.empty((N, 514, 514))
    all_interior_mask = np.empty((N, 512, 512), dtype='bool')
    for i, bid in enumerate(building_ids):
        u0, interior_mask = load_data(LOAD_DIR, bid)
        all_u0[i] = u0
        all_interior_mask[i] = interior_mask
    
    ts = time.time()
    with multiprocessing.Pool(n_proc) as pool:
        results_list = pool.starmap(process_floorplans, [(u, interior_mask, LOAD_DIR, MAX_ITER, ABS_TOL) 
                                                         for u, interior_mask in zip(split_array(all_u0,int(chunk_size)),
                                                                                     split_array(all_interior_mask,int(chunk_size)))])
    print(time.time() - ts)
    all_u = np.concatenate(results_list)
    '''
    # Print summary statistics in CSV format
    stat_keys = ['mean_temp', 'std_temp', 'pct_above_18', 'pct_below_15']
    print('building_id, ' + ', '.join(stat_keys))  # CSV header
    for bid, u, interior_mask in zip(building_ids, all_u, all_interior_mask):
        stats = summary_stats(u, interior_mask)
        print(f"{bid},", ", ".join(str(stats[k]) for k in stat_keys))
    '''