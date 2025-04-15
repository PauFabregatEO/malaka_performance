# save_domains.py

import numpy as np
from os.path import join


def load_data(load_dir, bid):
    SIZE = 512
    u = np.zeros((SIZE + 2, SIZE + 2))
    u[1:-1, 1:-1] = np.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask = np.load(join(load_dir, f"{bid}_interior.npy"))
    return u, interior_mask


LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'
SAVE_DIR = '/zhome/2c/a/213957/malaka_performance/source_MMB'  # adjust if needed

with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
    building_ids = f.read().splitlines()

N = 100
building_ids = building_ids[:N]

# Pre-allocate arrays
all_u0 = np.empty((N, 514, 514))  # padded domain images
all_interior_mask = np.empty((N, 512, 512), dtype=bool)  # interior masks

# Load and fill arrays
for i, bid in enumerate(building_ids):
    u0, interior_mask = load_data(LOAD_DIR, bid)
    all_u0[i] = u0
    all_interior_mask[i] = interior_mask

# Save to files
np.save(join(SAVE_DIR, 'image_domains.npy'), all_u0)
np.save(join(SAVE_DIR, 'interior_masks.npy'), all_interior_mask)

print("Saved 100 image domains and interior masks.")
