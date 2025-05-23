import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

# Read the data
df = pd.read_csv("computation.txt")

data = df[" mean_temp"]

# Fit a normal distribution: get mean (mu) and std (sigma)
mu, sigma = norm.fit(data)

# Plot the histogram
plt.hist(data, bins=20, density=True, alpha=0.6, color='skyblue', edgecolor='black', label='Histogram')

# Generate x values and corresponding PDF values
x = np.linspace(min(data), max(data), 100)
pdf = norm.pdf(x, mu, sigma)

# Plot the PDF
plt.plot(x, pdf, 'r-', label=f'Normal fit\nμ={mu:.2f}, σ={sigma:.2f}')

# Labels and legend
plt.title("Histogram of Mean Temperatures with Normal Fit")
plt.xlabel("Mean Temperature (°C)")
plt.ylabel("Density")
plt.legend()
plt.grid(True)
plt.savefig('temperature distribution.png', dpi=300)

# EXERCISE 2

average_mean_temp = df[" mean_temp"].mean()
print(f"Average Mean Temperature: {average_mean_temp:.2f} °C")

# EXERCISE 3

average_std_temp = df[" std_temp"].mean()
print(f"Average Temperature Standard Deviation: {average_std_temp:.2f}")

# EXERCISE 4

above_18 = df[df[" pct_above_18"] >= 50]
print(f"Number of buildings with ≥50% area above 18ºC: {len(above_18)}")

# EXERCISE 5

below_15 = df[df[" pct_below_15"] >= 50]
print(f"Number of buildings with ≥50% area below 15ºC: {len(below_15)}")
