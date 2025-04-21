import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import os

# Settings
name = 'Chunksize10'
filename = f'{name}.txt'
output_image = f'{name}.png'

# Load Data
n_iterations = []

if os.path.exists(filename):
    with open(filename, 'r') as file:
        for line in file:
            try:
                val = float(line.strip())
                n_iterations.append(val)
            except ValueError:
                continue
else:
    raise FileNotFoundError(f"File {filename} not found!")

n_iterations = np.array(n_iterations)

# Fit Normal Distribution 
mu, std = np.mean(n_iterations), np.std(n_iterations)

# Plot 
plt.figure(figsize=(10, 6))

# Histogram
plt.hist(n_iterations, bins=20, density=True, alpha=0.6, color='skyblue', edgecolor='black', label='Histogram')

# Normal distribution curve
x = np.linspace(min(n_iterations), max(n_iterations), 1000)
pdf = stats.norm.pdf(x, mu, std)
plt.plot(x, pdf, 'r', linewidth=2, label=f'Normal Fit\nμ={mu:.1f}, σ={std:.1f}')

# Add vertical line at the mean
peak_y = stats.norm.pdf(mu, mu, std)
plt.axvline(mu, color='black', linestyle='--', linewidth=1.5, label='Mean (μ)')
plt.plot(mu, peak_y, 'ko')  


plt.title(f'{filename}')
plt.xlabel('n_iterations')
plt.ylabel('Density')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(output_image, dpi=300)
plt.close()
