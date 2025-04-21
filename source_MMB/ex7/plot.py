import matplotlib.pyplot as plt
def plt_1(all_u,building_ids, index):
    plt.figure(figsize=(8, 6))
    plt.imshow(all_u[0][1:-1, 1:-1], cmap="hot", origin="lower")
    plt.colorbar(label="Temperature")
    plt.title(f"Temperature Distribution for Building {building_ids[0]}")
    plt.savefig(f"temperature_distribution{index}.png", dpi=300, bbox_inches="tight")
    plt.show()

def plt_2(all_u0, all_u):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].imshow(all_u0[0][1:-1, 1:-1], cmap="coolwarm", origin="lower")
    axes[0].set_title("Initial Temperature")
    axes[1].imshow(all_u[0][1:-1, 1:-1], cmap="coolwarm", origin="lower")
    axes[1].set_title("Final Temperature (After Jacobi)")

    for ax in axes:
        ax.set_xticks([])
        ax.set_yticks([])

    plt.colorbar(plt.cm.ScalarMappable(cmap="coolwarm"), ax=axes, location="right")
    plt.savefig("initial_vs_final.png", dpi=300, bbox_inches="tight")
    plt.show()

def plt_3(all_u,all_interior_mask,building_ids):
    plt.figure(figsize=(8, 6))
    plt.hist(all_u[0][1:-1, 1:-1][all_interior_mask[0]].flatten(), bins=30, color="royalblue", alpha=0.7)
    plt.xlabel("Temperature")
    plt.ylabel("Frequency")
    plt.title(f"Temperature Distribution Histogram for Building {building_ids[0]}")
    plt.savefig("temperature_histogram.png", dpi=300, bbox_inches="tight")
    plt.show()
