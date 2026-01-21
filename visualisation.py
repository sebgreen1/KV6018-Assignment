import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def visualise_packing(placed, container, title="Packing Solution"):
    """Visualise the circle packing"""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_aspect('equal')

    # Draw container boundary
    rect = patches.Rectangle(
        (0, 0),
        container.width,
        container.depth,
        linewidth=2,
        edgecolor='#F4BA02',
        facecolor='none'
    )
    ax.add_patch(rect)

    # Draw cylinders
    for i, c in enumerate(placed):
        circle = patches.Circle(
            (c['x'], c['y']),
            c['r'],
            facecolor='#99D9DD',
            edgecolor='#01364C',
            alpha=0.7
        )
        ax.add_patch(circle)

        # Label cylinder
        ax.text(
            c['x'], c['y'],
            str(i),
            ha='center',
            va='center',
            fontsize=9
        )

    ax.set_xlim(0, container.width)
    ax.set_ylim(0, container.depth)
    ax.set_title(title)
    ax.set_xlabel("Width")
    ax.set_ylabel("Depth")
    plt.tight_layout()
    plt.show()
