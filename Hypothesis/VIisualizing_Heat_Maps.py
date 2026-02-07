import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import TwoSlopeNorm
import numpy as np

def plot_velocity_heatmaps(heatmap_2024, heatmap_2025, figsize=(18, 12)):
    """
    Beautiful side-by-side + difference heatmap visualization.
    """
    # Prepare data
    days = heatmap_2024.index.tolist()  # ['Mon', 'Tue', ..., 'Sun']
    hours = heatmap_2024.columns.tolist()  # [0, 1, ..., 23]

    # Convert to numpy arrays for easier handling
    v2024 = heatmap_2024.to_numpy()
    v2025 = heatmap_2025.to_numpy()
    diff = v2025 - v2024

    # Global min/max for consistent color scale (excluding NaN)
    valid_2024 = v2024[~np.isnan(v2024)]
    valid_2025 = v2025[~np.isnan(v2025)]
    valid_diff = diff[~np.isnan(diff)]

    vmin = min(valid_2024.min(), valid_2025.min()) if len(valid_2024) > 0 else 0
    vmax = max(valid_2024.max(), valid_2025.max()) if len(valid_2024) > 0 else 30
    dmin, dmax = valid_diff.min(), valid_diff.max() if len(valid_diff) > 0 else (-10, 10)

    # Create figure with 3 subplots
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(2, 3, width_ratios=[1, 1, 0.08], wspace=0.3, hspace=0.25)

    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1, :2])
    cax1 = fig.add_subplot(gs[0, 2])
    cax3 = fig.add_subplot(gs[1, 2])

    # ── 2024 Heatmap ────────────────────────────────────────────────
    sns.heatmap(
        v2024, ax=ax1,
        cmap="viridis",  # or "YlGnBu" for yellow-green-blue
        vmin=vmin, vmax=vmax,
        annot=True, fmt=".1f",
        annot_kws={"size": 9, "weight": "bold"},
        cbar_ax=cax1,
        cbar_kws={"label": "Avg Speed (mph)", "shrink": 0.7},
        linewidths=0.5, linecolor="white",
        xticklabels=hours, yticklabels=days,
        square=True
    )
    ax1.set_title("Q1 2024 – Average Speed Inside Zone", fontsize=13, pad=10)
    ax1.set_xlabel("Hour of Day", fontsize=11)
    ax1.set_ylabel("Day of Week", fontsize=11)

    # ── 2025 Heatmap ────────────────────────────────────────────────
    sns.heatmap(
        v2025, ax=ax2,
        cmap="viridis",
        vmin=vmin, vmax=vmax,
        annot=True, fmt=".1f",
        annot_kws={"size": 9, "weight": "bold"},
        cbar=False,
        linewidths=0.5, linecolor="white",
        xticklabels=hours, yticklabels=days,
        square=True
    )
    ax2.set_title("Q1 2025 – Average Speed Inside Zone", fontsize=13, pad=10)
    ax2.set_xlabel("Hour of Day", fontsize=11)
    ax2.set_yticklabels([])  # hide y labels on right

    # ── Difference Heatmap (2025 – 2024) ────────────────────────────
    divnorm = TwoSlopeNorm(vmin=dmin, vcenter=0, vmax=dmax)
    sns.heatmap(
        diff, ax=ax3,
        cmap="RdBu_r",  # red = slower, blue = faster
        center=0,
        norm=divnorm,
        annot=True, fmt=".1f",
        annot_kws={"size": 9, "weight": "bold"},
        cbar_ax=cax3,
        cbar_kws={"label": "Speed Change (mph)", "shrink": 0.7},
        linewidths=0.5, linecolor="white",
        xticklabels=hours, yticklabels=days,
        square=True
    )
    ax3.set_title("Change: 2025 – 2024 (mph)", fontsize=13, pad=10)
    ax3.set_xlabel("Hour of Day", fontsize=11)
    ax3.set_ylabel("Day of Week", fontsize=11)

    # Overall figure title
    plt.suptitle(
        "Congestion Velocity Inside Pricing Zone\n"
        "Q1 2024 vs Q1 2025 – Average Speed by Hour & Day of Week",
        fontsize=16, fontweight="bold", y=1.02
    )

    # Save high-quality figure
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    output_file = "congestion_velocity_comparison.png"
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"\nHeatmap saved as: {output_file}")
    print("  • Left: Q1 2024 average speed")
    print("  • Middle: Q1 2025 average speed")
    print("  • Bottom: Speed difference (2025 – 2024)")
    print("  • Green/Blue tones = faster, Red = slower")