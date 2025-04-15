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

# @profile
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

def generate_chunks(num_workers, num_images, SCRIPT_NUMBER):
    '''This generates the indices'''
    items_chunk = num_images // (num_workers * SCRIPT_NUMBER)
    full_chunks = [items_chunk] * num_workers * SCRIPT_NUMBER
    for i, chunk in enumerate(full_chunks, start=1):
        full_chunks[i-1] = i * chunk 
    return full_chunks[:-1]
    


# This is the function passed to map
def jacobi_worker(chunked_temps, chunked_masks):
    # Allocate empty matrix for results
    result = np.empty((len(chunked_temps), 514, 514))
    for i, (u0, interior_mask) in enumerate(zip(chunked_temps, chunked_masks)):
        u = jacobi(u0, interior_mask, MAX_ITER, ABS_TOL)
        result[i] = u
    return result


def convert_results(results):
    global all_u
    np.copyto(all_u, np.concatenate(results, axis=0))



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
    with open(f"chunk_{SCRIPT_NUMBER}.txt", "w") as p:
        for n in range(len(y_speedup)):
                p.write(f'{y_speedup[n]}\n')


if __name__ == '__main__':

    # This corresponds to the division of the chunk to the n_images/n_proc which now is split further by SCRIPT_NUMBER
    # in this case chunk_size = n_images/(n_proc * 2)
    SCRIPT_NUMBER = 4

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

    for num_processes in range(1, MAX_PROC+1):
        # Time starts
        t = time()
        print(f"Entering {num_processes} process round...")
        chunk_indices = generate_chunks(num_processes, N, SCRIPT_NUMBER)
        # Generate both chunks
        temp_chunks = np.split(all_u0, chunk_indices)
        mask_chunks = np.split(all_interior_mask, chunk_indices)
        
        # Define workers to complete the Jacobi function
        worker = mp.Pool(processes=num_processes)
        print("Workers assigned")
        print("Entering starmap")
        results = worker.starmap(jacobi_worker, zip(temp_chunks, mask_chunks))
        t = time() - t
        # Allocate time into the time list
        time_proc[num_processes - 1] = t
        print(f"Closing workers for {num_processes} round...")
        worker.close()
        worker.join()
        print(f"{num_processes} workers closed!")
        
# All_u is now brought back to its original shape with all the data processed
convert_results(results)

# Plot the speed-up
compute_speedup(list(range(1, MAX_PROC + 1)), time_proc)

# Print summary statistics in CSV format
stat_keys = ['mean_temp', 'std_temp', 'pct_above_18', 'pct_below_15']
print('building_id, ' + ', '.join(stat_keys))  # CSV header
for bid, u, interior_mask in zip(building_ids, all_u, all_interior_mask):
    stats = summary_stats(u, interior_mask)
    print(f"{bid},", ", ".join(str(stats[k]) for k in stat_keys))

