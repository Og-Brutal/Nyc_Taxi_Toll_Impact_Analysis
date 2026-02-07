import pandas as pd

def get_congestion_zone_ids():
    csv_path = "/home/wahab/Data_Science_Assigment_1_final_draft/tlc_data/tlc_taxi_zone_lookup/taxi_zone_lookup.csv"

    congestion_ids = set()

    for chunk in pd.read_csv(csv_path, chunksize=1000):
        # Manhattan only
        manhattan = chunk[chunk["Borough"] == "Manhattan"]

        # Filter zones south of 60th St
        congestion = manhattan[
            ~manhattan["Zone"].str.contains(
                "Upper East|Upper West|Harlem|Washington Heights|Inwood",
                case=False,
                na=False
            )
        ]

        congestion_ids.update(congestion["LocationID"].tolist())

    return congestion_ids
