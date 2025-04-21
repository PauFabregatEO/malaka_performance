import matplotlib.pyplot as plt

# First, read the data

def reader(n):
    a = []
    with open(f'{n} images per chunk.txt', 'r') as file:
        for line in file:
            a.append(float(line.strip()))
    return a

def reader2():
    # Now, save the list as a text file 
    a = []
    with open('static chunk.txt', "r") as p:
        for n in p:
            a.append(float(n.strip()))
    return a

x = range(1, 21)


chunk1 = reader(1)
chunk2 = reader(2)
chunk3 = reader(4)
static_chunk = reader2()

# Plot
plt.figure(figsize=(10, 6))
plt.plot(x, chunk1, label='1 image/worker')
plt.plot(x, chunk2, label='2 images/worker')
plt.plot(x, chunk3, label='4 images/worker')
plt.plot(x, static_chunk, label='Static')

plt.title('Speed-up Comparison')
plt.xlabel('Number of Processors')
plt.ylabel('Speed-up')
plt.legend()
plt.grid(True)
plt.tight_layout()

# Save as PNG
plt.savefig('speedup_comparison.png', dpi=300)