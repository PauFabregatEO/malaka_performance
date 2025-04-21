from os.path import join
import sys
import numpy as np
import multiprocessing as mp
from time import perf_counter as time

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

def jacobi(u, interior_mask, max_iter, atol=1e-6):
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


def async_jacobi_worker(args):
    u0_all, mask_all = args
    u_compute = np.empty_like(u0_all)
    for i, (u0, mask) in enumerate(zip(u0_all, mask_all)):
        u_compute[i] = jacobi(u0, mask, MAX_ITER)
    return u_compute

def generate_chunks(num_workers, num_images):
    '''This generates the indices'''
    items_chunk = num_images // num_workers
    full_chunks = [items_chunk] * num_workers
    for i, chunk in enumerate(full_chunks, start=1):
        full_chunks[i-1] = i * chunk 
        full_chunks = full_chunks[:-1]
        full_chunks.append(N)
    return full_chunks

def compute_speedup(x, y):
    """
    Computes the speed-up and generates an image 
    
    Parameters:
    x (list): List of process counts (X-axis).
    y (list): List of execution times (Y-axis, reference-based speed-up).
    """
    if len(x) != len(y) or len(y) == 0:
        raise ValueError("Lists x and y must be of the same non-zero length")

    # Compute speed-up values: Speed-up = (first execution time) / (other execution times)
    y_speedup = [y[0] / val for val in y]

    # Now, save the list as a text file 
    with open('static chunk.txt', "w") as p:
        for n in range(len(y_speedup)):
                p.write(f'{y_speedup[n]}\n')


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
    all_u0 = np.empty((N, 514, 514))  # images are saved here N is the amount of images and 514, 514 determines its size
    all_interior_mask = np.empty((N, 512, 512), dtype='bool')
    for i, bid in enumerate(building_ids):
        u0, interior_mask = load_data(LOAD_DIR, bid)
        all_u0[i] = u0
        all_interior_mask[i] = interior_mask    # interior mask is 512x512 black and white

    # Run jacobi iterations for each floor plan
    MAX_ITER = 20_000
    ABS_TOL = 1e-4
    MAX_PROC = 20   # change this according to chosen CPU 

    # This is where the processed results will be stored
    all_u = np.empty_like(all_u0)
    # This list will process the time taken to solve the jacobi
    time_proc = np.empty(shape=MAX_PROC)


    # Now, usign apply_async
    for num_processes in range(1, MAX_PROC + 1):
        t = time()
        print(f"Running async with {num_processes} processes...")
        
        pool = mp.Pool(processes=num_processes)
        results = []
        slices = generate_chunks(num_processes, N)
        old = 0
        for i in slices:
            args = (all_u0[old: i], all_interior_mask[old: i])
            results.append(pool.apply_async(async_jacobi_worker, (args,)))
            # For indexing
            old = i
        # Collect results
        result_matrices = [r.get() for r in results]
        time_proc[num_processes - 1] = time() - t
        flattened_results = np.concatenate(result_matrices, axis=0)
        
        pool.close()
        pool.join()

        
        print(f"Finished async run with {num_processes} processes.")

        np.copyto(all_u, flattened_results)

# Save the speed-up in a text file
compute_speedup(list(range(1, MAX_PROC + 1)), time_proc)