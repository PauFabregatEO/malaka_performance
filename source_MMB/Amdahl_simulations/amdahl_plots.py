import matplotlib.pyplot as plt

# First, read the data

def reader(n):
    a = []
    with open(f'chunk_{n}.txt', 'r') as file:
        for line in file:
            a.append(float(line.strip()))
    return a


x = range(1, 21)

chunk1 = reader(1)
chunk2 = reader(2)
chunk3 = reader(3)
chunk4 = reader(4)
chunk5 = reader(5)

# Plot
plt.figure(figsize=(10, 6))
plt.plot(x, chunk1, label='Chunk Size = images/n_proc')
plt.plot(x, chunk2, label='Chunk Size /2')
plt.plot(x, chunk3, label='Chunk Size /3')
plt.plot(x, chunk4, label='Chunk Size /4')
plt.plot(x, chunk5, label='Chunk Size /5')

plt.title('Speed-up Comparison')
plt.xlabel('Number of Processors')
plt.ylabel('Speed-up')
plt.legend()
plt.grid(True)
plt.tight_layout()

# Save as PNG
plt.savefig('speedup_comparison.png', dpi=300) 