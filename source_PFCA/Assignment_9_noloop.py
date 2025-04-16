from os.path import join
import sys

import numpy as np
import cupy as cp
import matplotlib.pyplot as plt

import os

def load_data(load_dir, bid):
    SIZE = 512
    u = cp.zeros((SIZE + 2, SIZE + 2))  # Create a CuPy array
    # Load the .npy file using NumPy and convert it to CuPy
    u[1:-1, 1:-1] = cp.asarray(cp.load(join(load_dir, f"{bid}_domain.npy")))
    # Load the interior mask as a CuPy array
    interior_mask = cp.asarray(cp.load(join(load_dir, f"{bid}_interior.npy")))
    return u, interior_mask


def jacobi_3D(u, interior_mask, max_iter, atol=1e-6):
    u = cp.asarray(u)
    
    for i in range(max_iter):
        # Compute average of left, right, up and down neighbors, see eq. (1)
        #u_new = cp.array(0.25 * (u[vec_flag_3D,1:-1, :-2] + 
        #                         u[vec_flag_3D, 1:-1, 2:] + 
        #                         u[vec_flag_3D, :-2, 1:-1] + 
        #                         u[vec_flag_3D, 2:, 1:-1]))
        u_new = 0.25 * (u[:,1:-1, :-2] + 
                        u[:, 1:-1, 2:] + 
                        u[:, :-2, 1:-1] + 
                        u[:, 2:, 1:-1])

        #u_new_interior = cp.asarray(u_new[interior_mask[vec_flag_3D]])
        u[:,1:-1, 1:-1][interior_mask] = u_new[interior_mask]

        #print(interior_mask[vec_flag_3D].shape)
        #print(u[vec_flag_3D, 1:-1, 1:-1][interior_mask[vec_flag_3D]].shape)
        #print(u_new_interior.shape)

        #delta = cp.abs(u[vec_flag_3D, 1:-1, 1:-1][interior_mask[vec_flag_3D]] - u_new_interior).max(axis=(1,2))
        #u[:,1:-1, 1:-1][interior_mask] = u_new_interior

        #vec_flag_3D[vec_flag_3D] = ~(delta < atol)
        #if (delta < atol).all():
        #    break
    return u


def summary_stats(u, interior_mask):
    u_interior = u[1:-1, 1:-1][interior_mask]
    mean_temp = u_interior.mean()
    std_temp = u_interior.std()
    pct_above_18 = cp.sum(u_interior > 18) / u_interior.size * 100
    pct_below_15 = cp.sum(u_interior < 15) / u_interior.size * 100
    return {
        'mean_temp': mean_temp,
        'std_temp': std_temp,
        'pct_above_18': pct_above_18,
        'pct_below_15': pct_below_15,
    }

if __name__ == '__main__':
    # Load data
    LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'
    #print(os.path.exists(join(LOAD_DIR, "10000_domain.cpy")))
    with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
        building_ids = f.read().splitlines()

    if len(sys.argv) < 2:
        N = 1
    else:
        N = int(sys.argv[1])
    building_ids = building_ids[:N]

    # Load floor plans
    all_u0 = cp.empty((N, 514, 514))
    all_interior_mask = cp.empty((N, 512, 512), dtype='bool')
    for i, bid in enumerate(building_ids):
        u0, interior_mask = load_data(LOAD_DIR, bid)
        all_u0[i] = u0
        all_interior_mask[i] = interior_mask

    # Run jacobi iterations for each floor plan
    MAX_ITER = 20_000
    ABS_TOL = 1e-4

    # CHANGE: We pass the 3D matrix into the Jacobi function and handle it inside, instead of outisde
    #all_u = cp.empty_like(all_u0)
    all_u = jacobi_3D(all_u0, all_interior_mask, MAX_ITER, ABS_TOL)
    
    # Print summary statistics in CSV format
    stat_keys = ['mean_temp', 'std_temp', 'pct_above_18', 'pct_below_15']
    print('building_id, ' + ', '.join(stat_keys))  # CSV header
    for bid, u, interior_mask in zip(building_ids, all_u, all_interior_mask):
        stats = summary_stats(u, interior_mask)
        print(f"{bid},", ", ".join(str(stats[k]) for k in stat_keys))

    
        