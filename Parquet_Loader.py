# tlc_filters.py
import pyarrow.parquet as pq
import pandas as pd

def tlc_filtered_batches(file_path):
 

    # Columns of interest
    columns_of_interest = [
        "VendorID",
        "tpep_pickup_datetime",
        "lpep_pickup_datetime",
        "tpep_dropoff_datetime",
        "lpep_dropoff_datetime",
        "PULocationID",
        "DOLocationID",
        "trip_distance",
        "fare_amount",
        "total_amount",
        "congestion_surcharge",
        "tip_amount"
    ]

    # Mapping to unified column names
    cols_mapping = {
        "VendorID": "vendor_id",
        "tpep_pickup_datetime": "pickup_time",
        "lpep_pickup_datetime": "pickup_time",
        "tpep_dropoff_datetime": "dropoff_time",
        "lpep_dropoff_datetime": "dropoff_time",
        "PULocationID": "pickup_loc",
        "DOLocationID": "dropoff_loc",
        "trip_distance": "trip_distance",
        "fare_amount": "fare",
        "total_amount": "total_amount",
        "congestion_surcharge": "congestion_surcharge",
        "tip_amount": "tip_amount"
    }

    # Open Parquet file
    pq_file = pq.ParquetFile(file_path)
    total_rows = pq_file.metadata.num_rows
    batch_size = max(1, total_rows / 2) 
    # Batch iterator
    for batch in pq_file.iter_batches(batch_size=batch_size):
        df = batch.to_pandas()
        df = df[[col for col in columns_of_interest if col in df.columns]]
        df = df.rename(columns=cols_mapping)

        # Convert datetime columns
        df["pickup_time"] = pd.to_datetime(df["pickup_time"])
        df["dropoff_time"] = pd.to_datetime(df["dropoff_time"])

        # --- Apply Filters ---

        # 1. Teleporter
        df = df.query('(dropoff_time - pickup_time).dt.total_seconds() >= 60 and fare <= 20')

        # 2. Impossible Physics
        df = df.query('trip_distance / ((dropoff_time - pickup_time).dt.total_seconds() / 3600) <= 65')

        # 3. Stationary Ride
        df = df.query('trip_distance > 0 and fare > 0')


        if not df.empty:
            yield df
