# q1_yellow_vs_green_decline.py

import os
import pandas as pd
from collections import defaultdict
from Parquet_Loader import tlc_filtered_batches  # your batch generator


def get_q1_parquet_files(folder, year):
    """
    Return list of Q1 (Jan-Mar) parquet file paths in the folder.
    Expects filenames like: yellow_tripdata_YYYY-MM.parquet or green_tripdata_YYYY-MM.parquet
    """
    q1_files = []
    for filename in os.listdir(folder):
        if not filename.lower().endswith(".parquet"):
            continue

        # Normalize filename
        name_lower = filename.lower()
        if "tripdata" not in name_lower:
            continue

        # Extract year-month part (last part before .parquet)
        try:
            date_part = name_lower.split("_")[-1].replace(".parquet", "")
            y, m = date_part.split("-")
            y, m = int(y), int(m)
            if y == year and 1 <= m <= 3:
                full_path = os.path.join(folder, filename)
                q1_files.append(full_path)
        except (ValueError, IndexError):
            continue  # skip files that don't match pattern

    q1_files.sort()  # chronological order
    return q1_files


def trips_entering_zone(df, congestion_zone_ids):
    """Filter trips starting outside → ending inside the zone."""
    zone_set = set(congestion_zone_ids)  # faster .isin()
    return df[
        (~df["pickup_loc"].isin(zone_set)) &
        (df["dropoff_loc"].isin(zone_set))
    ]


def calculate_q1_entering_volumes(
    folder,
    congestion_zone_ids,
    year,
    taxi_type_column="taxi_type"   # ← change to "VendorID", "vendor_id", etc. if needed
):
    """
    Count Q1 entering trips, broken down by Yellow / Green.
    Only processes Jan–Mar files (should find 6 files per year).
    """
    counts = {"yellow": 0, "green": 0}
    total = 0

    q1_files = get_q1_parquet_files(folder, year)

    if not q1_files:
        print(f"Warning: No Q1 files (Jan-Mar) found for {year} in {folder}")
        print("Expected filenames like: yellow_tripdata_2024-01.parquet, green_tripdata_2024-01.parquet, etc.")
        return {"yellow": 0, "green": 0, "total": 0}

    print(f"Found {len(q1_files)} Q1 files for {year} (should be ~6):")
    for f in q1_files:
        print(f"  - {os.path.basename(f)}")

    for path in q1_files:
        filename = os.path.basename(path).lower()
        is_yellow = "yellow" in filename
        is_green  = "green"  in filename

        for df in tlc_filtered_batches(path):
            entering = trips_entering_zone(df, congestion_zone_ids)
            if entering.empty:
                continue

            trip_count = len(entering)

            # Classify by file name (more reliable than column if data is separated)
            if is_yellow:
                counts["yellow"] += trip_count
            elif is_green:
                counts["green"] += trip_count

            total += trip_count

    counts["total"] = total
    return counts


def compare_q1_yellow_vs_green(
    folder_2024,
    folder_2025,
    congestion_zone_ids,
    taxi_type_column="taxi_type"
):
    """Compare Q1 entering trips: 2024 vs 2025, Yellow vs Green."""
    print("=== Calculating Q1 2024 volumes ===")
    vol_2024 = calculate_q1_entering_volumes(folder_2024, congestion_zone_ids, 2024)

    print("\n=== Calculating Q1 2025 volumes ===")
    vol_2025 = calculate_q1_entering_volumes(folder_2025, congestion_zone_ids, 2025)

    def pct_change(old, new):
        if old == 0:
            return None if new == 0 else float('inf')
        return (new - old) / old * 100

    results = {
        "Yellow": {
            "Q1_2024": vol_2024["yellow"],
            "Q1_2025": vol_2025["yellow"],
            "change": vol_2025["yellow"] - vol_2024["yellow"],
            "pct_change": pct_change(vol_2024["yellow"], vol_2025["yellow"])
        },
        "Green": {
            "Q1_2024": vol_2024["green"],
            "Q1_2025": vol_2025["green"],
            "change": vol_2025["green"] - vol_2024["green"],
            "pct_change": pct_change(vol_2024["green"], vol_2025["green"])
        },
        "Total": {
            "Q1_2024": vol_2024["total"],
            "Q1_2025": vol_2025["total"],
            "change": vol_2025["total"] - vol_2024["total"],
            "pct_change": pct_change(vol_2024["total"], vol_2025["total"])
        }
    }

    return results


def print_comparison(results):
    """Pretty print the comparison."""
    print("\n" + "="*70)
    print("Q1 Entering Congestion Zone Trips: 2024 vs 2025 (Yellow vs Green Decline)")
    print("="*70)
    print(f"{'Type':<10} {'Q1 2024':>12} {'Q1 2025':>12} {'Change':>12} {'% Change':>12}")
    print("-"*70)

    for ttype, data in results.items():
        pct = f"{data['pct_change']:.1f}%" if data['pct_change'] is not None else "N/A"
        print(f"{ttype:<10} {data['Q1_2024']:12,} {data['Q1_2025']:12,} "
              f"{data['change']:12,} {pct:>12}")

    print("="*70)


    