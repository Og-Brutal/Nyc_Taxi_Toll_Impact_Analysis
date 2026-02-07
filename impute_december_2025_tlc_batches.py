import os
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from Parquet_Loader import tlc_filtered_batches

# ==========================================================
# CONFIG
# ==========================================================

BASE_DIR = "/home/wahab/Data_Science_Assigment_1_final_draft/tlc_data"

YEAR_2023 = os.path.join(BASE_DIR, "tlc_2023")
YEAR_2024 = os.path.join(BASE_DIR, "tlc_2024")
YEAR_2025 = os.path.join(BASE_DIR, "tlc_2025")

WEIGHT_2023 = 0.30
WEIGHT_2024 = 0.70

MONTH = "12"

# ==========================================================
# FULL TLC SCHEMA REQUIRED
# ==========================================================

FULL_SCHEMA_COLS = [
    "VendorID",
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
    "passenger_count",
    "trip_distance",
    "RatecodeID",
    "store_and_fwd_flag",
    "PULocationID",
    "DOLocationID",
    "payment_type",
    "fare_amount",
    "extra",
    "mta_tax",
    "tip_amount",
    "tolls_amount",
    "improvement_surcharge",
    "total_amount",
    "congestion_surcharge",
    "Airport_fee",
]

# ==========================================================
# LOAD ONE MONTH USING FILTERED BATCHES
# ==========================================================


def load_month(folder, taxi, year):
    path = os.path.join(folder, f"{taxi}_tripdata_{year}-{MONTH}.parquet")

    print(f"   loading {path}")

    dfs = []
    for batch in tlc_filtered_batches(path):
        dfs.append(batch)

    if not dfs:
        raise RuntimeError(f"No data loaded from {path}")

    return pd.concat(dfs, ignore_index=True)


# ==========================================================
# CONVERT FILTERED FORMAT → FULL TLC FORMAT
# ==========================================================


def restore_schema(df):
    df = df.copy()

    # Datetime rename (green taxi safety)
    if "lpep_pickup_datetime" in df.columns:
        df.rename(columns={
            "lpep_pickup_datetime": "tpep_pickup_datetime",
            "lpep_dropoff_datetime": "tpep_dropoff_datetime",
        }, inplace=True)

    if "pickup_time" in df.columns:
        df.rename(columns={
            "pickup_time": "tpep_pickup_datetime",
            "dropoff_time": "tpep_dropoff_datetime",
            "pickup_loc": "PULocationID",
            "dropoff_loc": "DOLocationID",
            "fare": "fare_amount",
        }, inplace=True)

    # Fill required columns
    for col in FULL_SCHEMA_COLS:
        if col not in df.columns:
            if col in ["Airport_fee"]:
                df[col] = 0.0
            else:
                df[col] = np.nan

    return df[FULL_SCHEMA_COLS]


# ==========================================================
# WEIGHTED IMPUTATION
# ==========================================================


def weighted_sample(df23, df24):
    n = int(len(df23) * WEIGHT_2023 + len(df24) * WEIGHT_2024)

    part23 = df23.sample(frac=WEIGHT_2023, replace=True, random_state=42)
    part24 = df24.sample(frac=WEIGHT_2024, replace=True, random_state=42)

    combined = pd.concat([part23, part24])
    combined = combined.sample(n=n, replace=True, random_state=99)

    return combined.reset_index(drop=True)


# ==========================================================
# IMPUTE ONE TAXI TYPE
# ==========================================================


def impute_taxi(taxi):

    print(f"\n🚕 Imputing December-2025 for {taxi.upper()}")

    df23 = load_month(YEAR_2023, taxi, 2023)
    df24 = load_month(YEAR_2024, taxi, 2024)

    print(
        f"   rows: 2023={len(df23)}  "
        f"2024={len(df24)} → "
        f"{int(len(df23)*WEIGHT_2023 + len(df24)*WEIGHT_2024)}"
    )

    df23 = restore_schema(df23)
    df24 = restore_schema(df24)

    combined = weighted_sample(df23, df24)

    out_path = os.path.join(
        YEAR_2025,
        f"{taxi}_tripdata_2025-12.parquet"
    )

    os.makedirs(YEAR_2025, exist_ok=True)

    table = pa.Table.from_pandas(combined)
    pq.write_table(table, out_path)

    print(f"✅ Written → {out_path}")


# ==========================================================
# MAIN ENTRY POINT
# ==========================================================


def impute_2025_12_data():

    print("\n==== PHASE 5 — DECEMBER-2025 IMPUTATION ====")

    for taxi in ["green", "yellow"]:
        impute_taxi(taxi)

    print("\n🎯 December-2025 Imputation COMPLETE\n")