import os
from pathlib import Path

def test_paths():
    root = Path(__file__).resolve().parent
    print(f"Root: {root}")
    
    tlc_data = root / "tlc_data"
    print(f"TLC Data Dir: {tlc_data} (Exists: {tlc_data.exists()})")
    
    if tlc_data.exists():
        for item in tlc_data.iterdir():
            if item.is_dir():
                parquet_files = list(item.glob("*.parquet"))
                print(f"  {item.name}: {len(parquet_files)} parquet files")

    # Test Hypothesis module path resolution
    hypo_file = root / "Hypothesis" / "Border_Effect.py"
    if hypo_file.exists():
        hypo_root = Path(hypo_file).resolve().parent.parent
        print(f"Hypothesis Root Resolution: {hypo_root}")
        print(f"Lookup CSV target: {hypo_root / 'tlc_data' / 'tlc_taxi_zone_lookup' / 'taxi_zone_lookup.csv'}")
        print(f"Lookup CSV exists: {(hypo_root / 'tlc_data' / 'tlc_taxi_zone_lookup' / 'taxi_zone_lookup.csv').exists()}")

if __name__ == "__main__":
    test_paths()
