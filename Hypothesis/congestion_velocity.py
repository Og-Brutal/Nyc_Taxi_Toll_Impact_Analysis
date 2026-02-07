# congestion_velocity.py

"""
Module to test the 'Congestion Velocity' hypothesis.

Computes average trip speed inside the congestion pricing zone
for Q1 of a given year and aggregates by:

- Hour of Day (0–23)
- Day of Week (Mon–Sun)

Designed to work with:
- Parquet_Loader.tlc_filtered_batches
- get_congestion_zone_location_ids.get_congestion_zone_ids
"""

import os
import sys
import pandas as pd
from collections import defaultdict
from pathlib import Path

# Ensure project root is in path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Parquet_Loader import tlc_filtered_batches
from get_congestion_zone_location_ids import get_congestion_zone_ids


# -------------------------------------------------------
# Helpers
# -------------------------------------------------------

Q1_MONTHS = {1, 2, 3}


def _list_parquet_files(folder):
    files = sorted(
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.endswith(".parquet")
    )
    print(f"Found {len(files)} parquet files in {folder}")
    return files


def _weekday_name(idx):
    return ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][idx]


# -------------------------------------------------------
# Main Computation
# -------------------------------------------------------

def compute_congestion_velocity_heatmap(
    parquet_folder,
    year_label=None,
):
    """
    Computes congestion-zone average speeds for Q1 only (January–March).

    Only processes parquet files corresponding to months 01, 02, 03.
    Avoids reading unnecessary files from April–December.

    Parameters
    ----------
    parquet_folder : str
        Folder containing monthly parquet files (yellow/green tripdata).

    year_label : str, optional
        Used only for labeling output.

    Returns
    -------
    heatmap_df : pd.DataFrame or None
        Index  = Day of Week (Mon–Sun)
        Columns = Hour of Day (0–23)
        Values = Avg Speed (mph)
        Returns None if no Q1 files are found.
    """

    if year_label:
        print(f"\n=== Processing {year_label} Q1 data ===")
    else:
        print("\n=== Processing congestion velocity data (Q1 only) ===")

    congestion_zone_ids = get_congestion_zone_ids()
    print(f"Loaded {len(congestion_zone_ids)} congestion zone IDs")

    # running totals
    speed_sum = defaultdict(float)
    count = defaultdict(int)

    total_trips_processed = 0
    total_inside_zone = 0

    # ───────────────────────────────────────────────────────────────
    # Only collect January (01), February (02), March (03) files
    # Supports both yellow_tripdata_YYYY-MM.parquet and green_tripdata_YYYY-MM.parquet
    # ───────────────────────────────────────────────────────────────
    q1_files = []
    for filename in sorted(os.listdir(parquet_folder)):
        if not filename.endswith(".parquet"):
            continue

        # Extract the month part from filename
        # Expected patterns: yellow_tripdata_2024-01.parquet  or  green_tripdata_2025-03.parquet
        base = filename.replace(".parquet", "")
        if "_" not in base:
            continue

        date_part = base.split("_")[-1]          # e.g. "2024-01" or "2025-03"
        if len(date_part) != 7 or date_part[4] != "-":
            continue

        month_str = date_part[5:7]               # "01", "02", "03", ...
        if month_str in {"01", "02", "03"}:
            full_path = os.path.join(parquet_folder, filename)
            q1_files.append(full_path)

    if not q1_files:
        print(f"ERROR: No Q1 (Jan–Mar) parquet files found in folder: {parquet_folder}")
        print("Expected files like: yellow_tripdata_YYYY-01.parquet, green_tripdata_YYYY-02.parquet, etc.")
        return None

    print(f"Found {len(q1_files)} Q1 files (Jan–Mar only) → processing only these.")

    for file_idx, path in enumerate(q1_files, 1):
        filename = os.path.basename(path)
        print(f"  [{file_idx}/{len(q1_files)}] Reading: {filename}")

        batch_count = 0
        for df in tlc_filtered_batches(path):
            batch_count += 1

            # Safety filter (in case filename logic ever misses something)
            df = df[df["pickup_time"].dt.month.isin(Q1_MONTHS)]
            if df.empty:
                continue

            total_trips_processed += len(df)

            # ---- inside congestion zone ----
            inside = df[
                df["pickup_loc"].isin(congestion_zone_ids)
                & df["dropoff_loc"].isin(congestion_zone_ids)
            ]

            if inside.empty:
                continue

            total_inside_zone += len(inside)

            # ---- trip duration in hours ----
            duration_hours = (
                inside["dropoff_time"] - inside["pickup_time"]
            ).dt.total_seconds() / 3600

            valid = duration_hours > 0
            inside = inside[valid].copy()
            duration_hours = duration_hours[valid]

            if inside.empty:
                continue

            speed = inside["trip_distance"] / duration_hours

            inside = inside.assign(speed=speed)

            # ---- time bins ----
            inside["hour"] = inside["pickup_time"].dt.hour
            inside["weekday"] = inside["pickup_time"].dt.weekday

            # ---- aggregate ----
            for (day, hour), grp in inside.groupby(["weekday", "hour"]):
                speed_sum[(day, hour)] += grp["speed"].sum()
                count[(day, hour)] += len(grp)

        print(f"    → Processed {batch_count} batches | "
              f"inside-zone trips so far: {total_inside_zone:,}")

    print(f"\nTotal trips processed (Q1 only): {total_trips_processed:,}")
    print(f"Total valid trips inside zone:    {total_inside_zone:,}")

    if total_inside_zone == 0:
        print("WARNING: No valid trips found inside the congestion zone.")
        return None

    # -------------------------------------------------------
    # Build heatmap table
    # -------------------------------------------------------

    print("Building final heatmap table...")

    rows = []
    for day in range(7):
        row = {"weekday": _weekday_name(day)}
        for hour in range(24):
            key = (day, hour)
            avg_speed = (
                speed_sum[key] / count[key]
                if count[key] > 0 else None
            )
            row[hour] = avg_speed
        rows.append(row)

    heatmap_df = pd.DataFrame(rows).set_index("weekday")

    # Final summary
    overall_avg = heatmap_df.values.mean()
    if pd.isna(overall_avg):
        print("No valid data to compute overall average speed.")
    else:
        print(f"Overall average speed inside zone: {overall_avg:.1f} mph")

    return heatmap_df


# -------------------------------------------------------
# Convenience Wrapper for 2024 vs 2025
# -------------------------------------------------------

def compare_q1_velocity(
    folder_2024,
    folder_2025,
):
    """
    Computes Q1 congestion-zone heatmaps for two years.
    Includes progress printing for both years.
    """
    print("Starting comparison of Q1 2024 vs Q1 2025 congestion velocity...")

    heatmap_2024 = compute_congestion_velocity_heatmap(folder_2024, "2024")
    heatmap_2025 = compute_congestion_velocity_heatmap(folder_2025, "2025")

    print("\nComparison complete.")
    return heatmap_2024, heatmap_2025