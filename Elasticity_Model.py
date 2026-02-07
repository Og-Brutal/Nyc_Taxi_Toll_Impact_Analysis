"""
Phase 4 — The Rain Tax
Rain Elasticity of Taxi Demand in NYC (2025)

• Fetch precipitation data for Central Park using Open-Meteo
• Aggregate TLC trips daily inside congestion zone
• Join weather + trips
• Compute elasticity proxy (correlation & regression)
• Plot wettest month: Daily Trips vs Rainfall
"""

import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress

from Crawler import TLCDownloader
from Parquet_Loader import tlc_filtered_batches
from zone_utils import get_congestion_zone_ids


# ============================================================
# CONFIG
# ============================================================

CENTRAL_PARK_LAT = 40.7812
CENTRAL_PARK_LON = -73.9665

WEATHER_CACHE = "weather_2025_central_park.csv"


# ============================================================
# WEATHER FETCHER — Open Meteo
# ============================================================

def fetch_precipitation_2025():

    if os.path.exists(WEATHER_CACHE):
        print("Loading cached weather data...")
        return pd.read_csv(WEATHER_CACHE, parse_dates=["date"])

    print("Fetching precipitation from Open-Meteo ARCHIVE...")

    url = (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={CENTRAL_PARK_LAT}"
        f"&longitude={CENTRAL_PARK_LON}"
        "&start_date=2025-01-01"
        "&end_date=2025-12-31"
        "&daily=precipitation_sum"
        "&timezone=America/New_York"
    )

    r = requests.get(url, timeout=30)
    r.raise_for_status()

    data = r.json()

    if "daily" not in data:
        raise RuntimeError(f"Unexpected weather API response: {data}")

    df = pd.DataFrame({
        "date": pd.to_datetime(data["daily"]["time"]),
        "precip_mm": data["daily"]["precipitation_sum"]
    })

    df.to_csv(WEATHER_CACHE, index=False)

    return df



# ============================================================
# TLC DAILY TRIP COUNTS (2025)
# ============================================================

def compute_daily_trip_counts_2025(tlc_2025_folder, congestion_zone_ids):

    daily_rows = []

    parquet_files = sorted(
        f for f in os.listdir(tlc_2025_folder)
        if f.endswith(".parquet")
    )

    print(f"Scanning {len(parquet_files)} TLC files...")

    for file in parquet_files:

        path = os.path.join(tlc_2025_folder, file)

        print(f"Processing: {file}")

        for batch in tlc_filtered_batches(path):

            if batch.empty:
                continue

            batch["pickup_time"] = pd.to_datetime(
                batch["pickup_time"],
                errors="coerce"
            )

            batch = batch.dropna(subset=["pickup_time"])

            batch = batch[
                batch["pickup_time"].dt.year == 2025
            ]

            if batch.empty:
                continue

            batch = batch[
                batch["pickup_loc"].isin(congestion_zone_ids)
            ]

            if batch.empty:
                continue

            batch["date"] = batch["pickup_time"].dt.date

            daily = batch.groupby("date").size().reset_index(name="trip_count")

            daily_rows.append(daily)

    if not daily_rows:
        return pd.DataFrame()

    combined = pd.concat(daily_rows)

    combined = (
        combined.groupby("date")["trip_count"]
        .sum()
        .reset_index()
    )

    combined["date"] = pd.to_datetime(combined["date"])

    return combined


# ============================================================
# JOIN WEATHER + TLC
# ============================================================

def merge_weather_trips(weather_df, trip_df):

    merged = pd.merge(
        weather_df,
        trip_df,
        on="date",
        how="inner"
    )

    return merged.sort_values("date")


# ============================================================
# ELASTICITY METRICS
# ============================================================

def compute_rain_elasticity(df):

    slope, intercept, r, p, stderr = linregress(
        df["precip_mm"],
        df["trip_count"]
    )

    return {
        "slope": slope,
        "correlation": r,
        "p_value": p,
        "stderr": stderr
    }


# ============================================================
# WETTEST MONTH VISUALIZATION
# ============================================================

def plot_wettest_month(df):

    df["month"] = df["date"].dt.to_period("M")

    wettest = (
        df.groupby("month")["precip_mm"]
        .sum()
        .idxmax()
    )

    wet_df = df[df["month"] == wettest]

    print(f"\nWettest Month of 2025: {wettest}")

    plt.figure(figsize=(14, 7))

    plt.scatter(
        wet_df["precip_mm"],
        wet_df["trip_count"],
        s=60
    )

    slope, intercept, r, _, _ = linregress(
        wet_df["precip_mm"],
        wet_df["trip_count"]
    )

    x = wet_df["precip_mm"]
    y = intercept + slope * x

    plt.plot(x, y, linewidth=2, label=f"Fit Line (r={r:.2f})")

    plt.xlabel("Daily Precipitation (mm)")
    plt.ylabel("Daily Trip Count")
    plt.title(
        f"Rain Elasticity of Demand — {wettest}\n"
        "Central Park Precipitation vs Taxi Trips"
    )

    plt.legend()
    plt.tight_layout()
    plt.show()


# ============================================================
# MAIN DRIVER
# ============================================================

def run_weather_elastisity():

    print("\n==== PHASE 4 — RAIN TAX ANALYSIS ====\n")

    zones = get_congestion_zone_ids()

    # Optional: ensure TLC data downloaded
    # downloader = TLCDownloader(year=2025)
    # downloader.download_all()

    weather_df = fetch_precipitation_2025()

    trip_df = compute_daily_trip_counts_2025(
        tlc_2025_folder="tlc_data/tlc_2025",
        congestion_zone_ids=zones
    )

    if trip_df.empty:
        raise RuntimeError("No TLC trips found for 2025!")

    merged = merge_weather_trips(weather_df, trip_df)

    elasticity = compute_rain_elasticity(merged)

    print("\n==== Rain Elasticity Results (2025) ====")
    print(f"Slope (Trips per mm rain): {elasticity['slope']:.2f}")
    print(f"Correlation r: {elasticity['correlation']:.3f}")
    print(f"P-value: {elasticity['p_value']:.5f}")

    plot_wettest_month(merged)

    # Return results for programmatic use (PDF, reports, etc.)
    return {
        "slope": elasticity["slope"],
        "correlation": elasticity["correlation"],
        "p_value": elasticity["p_value"],
        "stderr": elasticity["stderr"]
    }


