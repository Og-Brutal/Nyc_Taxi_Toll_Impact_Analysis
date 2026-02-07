# border_effect_choropleth.py
"""
Phase 3 - Border Effect: % Change in Drop-offs in zones just north of congestion zone
Q1 2024 vs Q1 2025

Visualization: Matplotlib + GeoPandas only (no Folium/HTML)
"""

import os
import pandas as pd
from collections import defaultdict
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

# ──────────────────────────────────────────────
# Reuse your existing modules (no duplication)
# ──────────────────────────────────────────────
import sys
from pathlib import Path

# Project constants
PROJECT_ROOT = Path(__file__).resolve().parent.parent

from Parquet_Loader import tlc_filtered_batches           # your batch loader
from zone_utils import get_congestion_zone_ids  # your function

FOLDER_2024 = str(PROJECT_ROOT / "tlc_data" / "tlc_2024")
FOLDER_2025 = str(PROJECT_ROOT / "tlc_data" / "tlc_2025")

LOOKUP_CSV = str(PROJECT_ROOT / "tlc_data" / "tlc_taxi_zone_lookup" / "taxi_zone_lookup.csv")
SHAPEFILE_ZIP = "taxi_zones.zip"

# Zones considered "just outside" (north of ~60th St)
BORDERING_ZONE_PATTERNS = [
    "Upper East Side", "Upper West Side", "Manhattan Valley",
    "Yorkville", "Lenox Hill", "Lincoln Square", "Central Park"
]


def download_shapefile_if_missing():
    """Download taxi_zones.zip if missing (basic requests version)"""
    if os.path.exists(SHAPEFILE_ZIP):
        print(f"Shapefile already exists: {SHAPEFILE_ZIP}")
        return

    import requests
    url = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zones.zip"
    print(f"Downloading shapefile from {url} ...")
    r = requests.get(url)
    r.raise_for_status()
    with open(SHAPEFILE_ZIP, "wb") as f:
        f.write(r.content)
    print("Download complete.")


def get_bordering_zone_ids():
    inner_zone_ids = get_congestion_zone_ids()
    df = pd.read_csv(LOOKUP_CSV)

    candidates = df[
        (df["Borough"] == "Manhattan") &
        df["Zone"].str.contains("|".join(BORDERING_ZONE_PATTERNS), case=False, na=False)
    ]

    border_ids = set(candidates["LocationID"]) - set(inner_zone_ids)

    print(f"Selected {len(border_ids)} probable bordering zones")
    print("Bordering LocationIDs:", sorted(border_ids))

    return border_ids


def count_q1_dropoffs(folder: str, year: int, target_zone_ids: set):
    counts = defaultdict(int)

    q1_files = []
    for fname in os.listdir(folder):
        if not fname.lower().endswith(".parquet"): continue
        if "tripdata" not in fname.lower(): continue
        try:
            date_part = fname.lower().split("_")[-1].replace(".parquet", "")
            y, m = map(int, date_part.split("-"))
            if y == year and 1 <= m <= 3:
                q1_files.append(os.path.join(folder, fname))
        except:
            pass

    if not q1_files:
        print(f"No Q1 files found in {folder} for {year}")
        return dict(counts)

    q1_files.sort()
    print(f"→ Found {len(q1_files)} Q1 files for {year}")

    for path in q1_files:
        print(f"  Reading: {os.path.basename(path)}")
        for df in tlc_filtered_batches(path):
            mask = df["dropoff_loc"].isin(target_zone_ids)
            if not mask.any():
                continue
            zone_counts = df.loc[mask, "dropoff_loc"].value_counts()
            for loc_id, cnt in zone_counts.items():
                counts[loc_id] += cnt

    return dict(counts)


def calculate_border_dropoff_changes():
    border_ids = get_bordering_zone_ids()

    print("\n=== Counting drop-offs Q1 2024 ===")
    counts_2024 = count_q1_dropoffs(FOLDER_2024, 2024, border_ids)

    print("\n=== Counting drop-offs Q1 2025 ===")
    counts_2025 = count_q1_dropoffs(FOLDER_2025, 2025, border_ids)

    data = []
    all_zones = sorted(set(counts_2024) | set(counts_2025))

    for loc in all_zones:
        c24 = counts_2024.get(loc, 0)
        c25 = counts_2025.get(loc, 0)
        diff = c25 - c24
        pct = round((diff / c24 * 100), 1) if c24 > 0 else None

        data.append({
            "LocationID": loc,
            "Dropoffs_2024": c24,
            "Dropoffs_2025": c25,
            "Change": diff,
            "% Change": pct
        })

    df = pd.DataFrame(data)
    return df, border_ids


def generate_choropleth(df: pd.DataFrame):
    """
    Create static choropleth using Matplotlib + GeoPandas only.
    Handles cases where all values are positive or negative.
    """
    download_shapefile_if_missing()

    extract_dir = "taxi_zones_shp"
    if not os.path.exists(extract_dir):
        from zipfile import ZipFile
        with ZipFile(SHAPEFILE_ZIP, 'r') as z:
            z.extractall(extract_dir)
        print(f"Shapefile extracted to: {extract_dir}")

    shp_path = f"{extract_dir}/taxi_zones.shp"
    if not os.path.exists(shp_path):
        print(f"Error: Shapefile not found at {shp_path}")
        return

    gdf = gpd.read_file(shp_path)
    print("Shapefile loaded successfully.")

    # Force string match
    gdf["LocationID"] = gdf["LocationID"].astype(str).str.strip()
    df["LocationID"] = df["LocationID"].astype(str).str.strip()

    merged = gdf.merge(df, on="LocationID", how="inner")

    # ── DEBUG PRINTS ────────────────────────────────────────────────
    print("\n=== DEBUG INFO ===")
    print("Number of rows in original df:", len(df))
    print("Number of rows in gdf (all zones):", len(gdf))
    print("Number of rows after merge:", len(merged))
    print("Merged columns:", merged.columns.tolist())

    if not merged.empty:
        print("Sample of merged data:")
        print(merged[["LocationID", "zone", "% Change"]].head().to_string(index=False))
    else:
        print("MERGED IS EMPTY → no zones matched")
        print("Your df LocationIDs:", sorted(df["LocationID"].unique()))
        print("Shapefile LocationIDs sample (first 10):",
              sorted(gdf["LocationID"].unique())[:10])
        return

    # ── Matplotlib Plot ─────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(12, 14))

    # Choose appropriate normalization based on data range
    pct_values = merged["% Change"].dropna()
    if pct_values.empty:
        print("No valid % Change values → using default colormap")
        norm = None
    else:
        vmin = pct_values.min()
        vmax = pct_values.max()

        if vmin >= 0:
            # All positive → use simple linear norm, green to dark green
            norm = plt.Normalize(vmin=vmin, vmax=vmax)
            cmap = "Greens"
        elif vmax <= 0:
            # All negative → red to dark red
            norm = plt.Normalize(vmin=vmin, vmax=vmax)
            cmap = "Reds_r"
        else:
            # Mixed signs → center at 0
            abs_max = max(abs(vmin), abs(vmax))
            norm = TwoSlopeNorm(vmin=-abs_max, vcenter=0, vmax=abs_max)
            cmap = "RdYlGn_r"

    merged.plot(
        column="% Change",
        ax=ax,
        legend=True,
        cmap=cmap,
        norm=norm,
        edgecolor="black",
        linewidth=0.6,
        legend_kwds={
            "label": "% Change in Drop-offs (Q1 2024 → Q1 2025)",
            "orientation": "horizontal",
            "pad": 0.01,
            "shrink": 0.6,
            "aspect": 30
        },
        missing_kwds={"color": "lightgrey"}
    )

    # Add zone labels inside polygons
    for idx, row in merged.iterrows():
        if pd.notna(row["% Change"]):
            centroid = row.geometry.centroid
            label = f"{row['LocationID']}\n{row['zone'][:18]}...\n{row['% Change']}%"
            ax.annotate(
                text=label,
                xy=(centroid.x, centroid.y),
                xytext=(0, 0),
                textcoords="offset points",
                ha="center", va="center",
                fontsize=8, color="black", weight="bold",
                bbox=dict(facecolor="white", alpha=0.75, edgecolor="none", pad=1.5)
            )

    ax.set_title("Border Effect – % Change in Drop-offs\nZones North of Congestion Boundary (Q1 2024 vs 2025)",
                 fontsize=14, pad=20)
    ax.axis("off")

    plt.tight_layout()
    output_file = "border_effect_choropleth_matplotlib.png"
    plt.savefig(output_file, dpi=200, bbox_inches="tight")
    plt.close(fig)

    print(f"\nStatic choropleth map saved → {output_file}")
    print("Zones colored: green = increase, red = decrease, grey = no data")
    print("Labels show ID, zone name, and % change.")


def generate_interactive_folium_map(df: pd.DataFrame):
    """
    Create interactive Folium map for Border Effect visualization.
    Returns the map object and saves as HTML file.
    """
    try:
        import folium
        from folium import GeoJson, Choropleth
        import json
    except ImportError:
        print("ERROR: folium not installed. Run: pip install folium")
        return None
    
    download_shapefile_if_missing()
    
    extract_dir = "taxi_zones_shp"
    if not os.path.exists(extract_dir):
        from zipfile import ZipFile
        with ZipFile(SHAPEFILE_ZIP, 'r') as z:
            z.extractall(extract_dir)
        print(f"Shapefile extracted to: {extract_dir}")
    
    shp_path = f"{extract_dir}/taxi_zones.shp"
    if not os.path.exists(shp_path):
        print(f"Error: Shapefile not found at {shp_path}")
        return None
    
    gdf = gpd.read_file(shp_path)
    print("Shapefile loaded for interactive map.")
    
    # Force string match
    gdf["LocationID"] = gdf["LocationID"].astype(str).str.strip()
    df["LocationID"] = df["LocationID"].astype(str).str.strip()
    
    merged = gdf.merge(df, on="LocationID", how="inner")
    
    if merged.empty:
        print("ERROR: No zones matched for interactive map")
        return None
    
    # Convert to WGS84 for Folium
    merged = merged.to_crs(epsg=4326)
    
    # Calculate map center
    bounds = merged.total_bounds
    center_lat = (bounds[1] + bounds[3]) / 2
    center_lon = (bounds[0] + bounds[2]) / 2
    
    # Create base map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        tiles='CartoDB positron'
    )
    
    # Determine color scale
    pct_values = merged["% Change"].dropna()
    if not pct_values.empty:
        vmin = pct_values.min()
        vmax = pct_values.max()
        
        # Create color function
        def get_color(pct_change):
            if pd.isna(pct_change):
                return '#cccccc'  # grey for no data
            
            if vmin >= 0:
                # All positive - green scale
                normalized = (pct_change - vmin) / (vmax - vmin) if vmax > vmin else 0.5
                intensity = int(255 * (1 - normalized * 0.7))
                return f'#00{intensity:02x}00'
            elif vmax <= 0:
                # All negative - red scale
                normalized = (pct_change - vmin) / (vmax - vmin) if vmax > vmin else 0.5
                intensity = int(255 * (1 - normalized * 0.7))
                return f'#{intensity:02x}0000'
            else:
                # Mixed - red to green
                if pct_change < 0:
                    intensity = int(255 * abs(pct_change) / abs(vmin))
                    return f'#{min(255, intensity):02x}0000'
                else:
                    intensity = int(255 * pct_change / vmax)
                    return f'#00{min(255, intensity):02x}00'
    else:
        def get_color(pct_change):
            return '#cccccc'
    
    # Add zones to map
    for idx, row in merged.iterrows():
        # Create tooltip
        tooltip_text = f"""
        <div style="font-family: Arial; font-size: 12px;">
            <b>{row['zone']}</b><br>
            Location ID: {row['LocationID']}<br>
            <hr style="margin: 5px 0;">
            Drop-offs 2024: {row['Dropoffs_2024']:,}<br>
            Drop-offs 2025: {row['Dropoffs_2025']:,}<br>
            Change: {row['Change']:+,}<br>
            <b>% Change: {row['% Change']:.1f}%</b>
        </div>
        """
        
        # Get color for this zone
        color = get_color(row['% Change'])
        
        # Add polygon
        folium.GeoJson(
            row['geometry'],
            style_function=lambda x, color=color: {
                'fillColor': color,
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.7
            },
            tooltip=folium.Tooltip(tooltip_text, sticky=True)
        ).add_to(m)
    
    # Add title
    title_html = '''
    <div style="position: fixed; 
                top: 10px; left: 50px; width: 500px; height: 90px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px; border-radius: 5px;">
        <h4 style="margin: 0;">Border Effect - % Change in Drop-offs</h4>
        <p style="margin: 5px 0; font-size: 12px;">
            Zones North of Congestion Boundary (Q1 2024 vs 2025)<br>
            <span style="color: green;">■</span> Increase 
            <span style="color: red;">■</span> Decrease
            <span style="color: grey;">■</span> No Data
        </p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Save map
    output_file = "border_effect_map.html"
    m.save(output_file)
    print(f"\nInteractive Folium map saved → {output_file}")
    print("Map includes clickable zones with detailed tooltips.")
    
    return m



   