import pandas as pd
import matplotlib.pyplot as plt

# import debugpy

# debugpy.listen(('0.0.0.0', 5677))
# print('Wait for debugger...')
# debugpy.wait_for_client()
# print('Connected!')

# Read the data
df = pd.read_csv("computation.txt")

# Show the first few rows to verify
print(df.head())


# EXERCISE 1

plt.hist(df[" mean_temp"], bins=20, color='skyblue', edgecolor='black')
plt.title("Distribution of Mean Temperatures")
plt.xlabel("Mean Temperature (°C)")
plt.ylabel("Number of Buildings")
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
