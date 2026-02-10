# leakage_audit.py

from collections import defaultdict
import os
import pandas as pd
from Parquet_Loader import tlc_filtered_batches

def run_leakage_audit(
    parquet_folder,
    congestion_zone_ids,
    after_date="2025-01-05",
):
    """
    Runs leakage audit on all parquet files using batch generator.

    Returns:
        compliance_rate (float)
        top3_missing (pd.DataFrame)
    """

    total_should_pay = 0
    total_paid = 0

    missing_by_pickup = defaultdict(int)
    total_by_pickup = defaultdict(int)

    # ---- get all Parquet files ----
    parquet_files = sorted(
        [
            os.path.join(parquet_folder, f)
            for f in os.listdir(parquet_folder)
            if f.endswith(".parquet")
        ]
    )
    if not parquet_files:
        print("No parquet files found.")
        return 0, pd.DataFrame()

    # ---- process all files ----
    for file_idx, file_path in enumerate(parquet_files):
        print(f"Processing file {file_idx+1}/{len(parquet_files)}: {file_path}")

        # ---- process all batches ----
        for batch_idx, df in enumerate(tlc_filtered_batches(file_path)):
            # ---- filter after toll date ----
            df = df[df["pickup_time"] >= after_date]

            # ---- trips involving congestion zone ----
            # Including any trip that ends in the zone (even if it started inside)
            # to match the user's expected audit scope.
            entering = df[df["dropoff_loc"].isin(congestion_zone_ids)]

            if entering.empty:
                continue

            total_should_pay += len(entering)
            paid_mask = entering["congestion_surcharge"].fillna(0) > 0
            total_paid += paid_mask.sum()

            # ---- group by pickup location ----
            grouped = entering.groupby("pickup_loc").agg(
                total_trips=pd.NamedAgg(column="pickup_loc", aggfunc="count"),
                missing_trips=pd.NamedAgg(
                    column="congestion_surcharge",
                    aggfunc=lambda x: (x == 0).sum()
                )
            )

            # ---- accumulate totals per pickup location ----
            for loc, row in grouped.iterrows():
                total_by_pickup[loc] += row["total_trips"]
                missing_by_pickup[loc] += row["missing_trips"]

    # ----------------------------
    # FINAL CALCULATIONS
    # ----------------------------

    # Compliance rate for all trips entering the zone
    compliance_rate = total_paid / total_should_pay if total_should_pay else 0

    # Create DataFrame for top 3 pickup locations with highest missing rate
    # Using the location IDs as the index directly
    pickup_df = pd.DataFrame({
        "total_trips": pd.Series(total_by_pickup),
        "missing_trips": pd.Series(missing_by_pickup),
    })

    # Filter out any locations with zero trips to avoid division by zero
    pickup_df = pickup_df[pickup_df["total_trips"] > 0]

    # Missing rate calculation
    pickup_df["missing_rate"] = pickup_df["missing_trips"] / pickup_df["total_trips"]

    # Top 3 locations with highest missing surcharge rate
    top3_missing = pickup_df.sort_values("missing_rate", ascending=False).head(3)

    return compliance_rate, top3_missing
