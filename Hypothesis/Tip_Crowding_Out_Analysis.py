import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Project constants
PROJECT_ROOT = Path(__file__).resolve().parent.parent

from Parquet_Loader import tlc_filtered_batches
from zone_utils import get_congestion_zone_ids
from scipy.stats import linregress

# ============================================================
# Helper: compute tip percentage safely
# ============================================================

def compute_tip_percent(df):

    df = df.copy()
    df["tip_percent"] = 0.0

    fare_col = "fare_amount" if "fare_amount" in df.columns else "fare"

    if fare_col not in df.columns:
        raise ValueError("No fare column found!")

    if "tip_amount" in df.columns:

        valid = (df[fare_col] > 0) & df["tip_amount"].notna()

        df.loc[valid, "tip_percent"] = (
            df.loc[valid, "tip_amount"] / df.loc[valid, fare_col]
        ) * 100

    return df

# ============================================================
# Process one parquet file (2025 only)
# ============================================================

def process_parquet_file_2025(
    parquet_path,
    congestion_zone_ids,
    after_date="2025-01-05"
):

    monthly_rows = []

    filename = os.path.basename(parquet_path)
    print(f"  Reading: {filename}")

    for batch in tlc_filtered_batches(parquet_path):

        if batch.empty:
            continue

        # Ensure datetime
        batch["pickup_time"] = pd.to_datetime(batch["pickup_time"], errors="coerce")
        batch = batch.dropna(subset=["pickup_time"])

        # 2025 ONLY
        batch = batch[batch["pickup_time"].dt.year == 2025]
        if batch.empty:
            continue

        # Apply toll start date
        cutoff = pd.to_datetime(after_date)
        batch = batch[batch["pickup_time"] >= cutoff]
        if batch.empty:
            continue

        # Congestion zone only
        batch = batch[batch["pickup_loc"].isin(congestion_zone_ids)]
        if batch.empty:
            continue

        # Month
        batch.loc[:, "month"] = batch["pickup_time"].dt.to_period("M")

        # Compute tip %
        batch = compute_tip_percent(batch)

        # Surcharge column safety
        surcharge_col = "congestion_surcharge" if "congestion_surcharge" in batch.columns else "congestion_surcharge_amount"
        if surcharge_col not in batch.columns:
            raise ValueError("No congestion surcharge column found!")

        # Monthly aggregation
        monthly = batch.groupby("month").agg(
            avg_surcharge=(surcharge_col, "mean"),
            avg_tip_percent=("tip_percent", "mean"),
            trip_count=("month", "count")
        )

        monthly_rows.append(monthly)

    if not monthly_rows:
        return pd.DataFrame()

    combined = pd.concat(monthly_rows)
    return combined.groupby("month").mean(numeric_only=True)

# ============================================================
# Scan 2025 folder
# ============================================================

def aggregate_2025_folder(tlc_2025_folder, congestion_zone_ids, after_date="2025-01-05"):

    results = []

    parquet_files = sorted(f for f in os.listdir(tlc_2025_folder) if f.endswith(".parquet"))
    print(f"Found {len(parquet_files)} parquet files in {tlc_2025_folder}")

    for file in parquet_files:
        path = os.path.join(tlc_2025_folder, file)
        print(f"Processing: {file}")

        monthly = process_parquet_file_2025(path, congestion_zone_ids, after_date)
        if not monthly.empty:
            results.append(monthly)

    if not results:
        return pd.DataFrame()

    combined = pd.concat(results)
    return combined.groupby("month").mean(numeric_only=True)

# ============================================================
# MAIN DRIVER — 2025 ONLY + Correlation & Scatter
# ============================================================

def run_tip_crowding_out_2025_with_scatter(tlc_2025_folder, congestion_zone_ids, after_date="2025-01-05"):

    print("\n==== Processing 2025 Only (Post-Toll) ====")

    combined = aggregate_2025_folder(tlc_2025_folder, congestion_zone_ids, after_date)
    if combined.empty:
        print("No usable 2025 data found.")
        return pd.DataFrame()

    combined = combined.sort_index()
    print("\nFinal Monthly Table — 2025:")
    print(combined.round(2))

    # ================================
    # Dual-axis Monthly Trend Chart
    # ================================
    fig, ax1 = plt.subplots(figsize=(14, 7))
    months = combined.index.astype(str)

    ax1.bar(months, combined["avg_surcharge"], alpha=0.6, label="Avg Congestion Surcharge ($)")
    ax1.set_ylabel("Avg Surcharge ($)")
    ax1.set_xlabel("Month")

    ax2 = ax1.twinx()
    ax2.plot(months, combined["avg_tip_percent"], marker="o", linewidth=2.5, label="Avg Tip %")
    ax2.set_ylabel("Avg Tip (%)")

    plt.title("Tip Crowding-Out Hypothesis (2025 Only)\nCongestion Surcharge vs Tip Percentage — Congestion Zone Pickups")
    fig.autofmt_xdate(rotation=45)
    ax1.legend(loc="upper left")
    ax2.legend(loc="upper right")
    plt.tight_layout()
    plt.show()

    # ================================
    # Scatter Plot + Regression
    # ================================
    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        x=combined["avg_surcharge"],
        y=combined["avg_tip_percent"],
        s=100,
        color="blue"
    )

    # Linear regression line
    slope, intercept, r_value, p_value, std_err = linregress(
        combined["avg_surcharge"], combined["avg_tip_percent"]
    )
    x_vals = combined["avg_surcharge"]
    y_vals = intercept + slope * x_vals
    plt.plot(x_vals, y_vals, color="red", linewidth=2, label=f"Fit line (r={r_value:.2f})")

    plt.xlabel("Avg Congestion Surcharge ($)")
    plt.ylabel("Avg Tip (%)")
    plt.title("Scatter: Avg Surcharge vs Avg Tip % (2025 Post-Toll)")
    plt.legend()
    plt.tight_layout()
    plt.show()

    print(f"\nCorrelation coefficient (r) = {r_value:.2f}, p-value = {p_value:.4f}")

    return combined
