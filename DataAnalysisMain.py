from Crawler import TLCDownloader
from Parquet_Loader import tlc_filtered_batches
from get_congestion_zone_location_ids import get_congestion_zone_ids
import pandas as pd
from Leakage_Audit import run_leakage_audit
from Yellow_vs_Green_Decline import (
    compare_q1_yellow_vs_green,
    print_comparison
)
from Hypothesis.Border_Effect import (
    calculate_border_dropoff_changes,   
    generate_choropleth,   
)
from Hypothesis.congestion_velocity import compare_q1_velocity
from Hypothesis.VIisualizing_Heat_Maps import plot_velocity_heatmaps
from Hypothesis.Tip_Crowding_Out_Analysis import run_tip_crowding_out_2025_with_scatter
from Elasticity_Model import run_weather_elastisity
from impute_december_2025_tlc_batches import impute_2025_12_data
from generate_audit_report import run_audit_report


# python3 -m streamlit run streamlit_dashboard.py



# Phase 01

# Scraping Data
# downloader = TLCDownloader(base_download_dir="tlc_data")
# folder=downloader.get_folder("taxi_zone_lookup")
# downloader.download_year(2023, taxi_types=("yellow", "green"))
# downloader.download_year(2024, taxi_types=("yellow", "green"))
# downloader.download_year(2025, taxi_types=("yellow", "green"))
# downloader.download_file("https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv",folder)
# impute_2025_12_data()


#Loading Filterd Data in Batches
# generatorObject=tlc_filtered_batches("/home/wahab/Data_Science_Assigment_1_final_draft/tlc_data/tlc_parquet_2025/green_tripdata_2025-04.parquet")
# df=next(generatorObject)



# Phase 02


# Getting congestion zone's location ids 
# congestionZoneIds=get_congestion_zone_ids()

# Compilance Rate and top 3 pickup locations with the highest rate of "missing surcharges."
# (compliance_rate,top3_missing)=run_leakage_audit("/home/wahab/Data_Science_Assigment_1_final_draft/tlc_data/tlc_2025"
#                                                  ,congestion_zone_ids=congestionZoneIds
#                                                  ,after_date="2025-01-05"
#                                                  )
# print("Compilance Rate : ",compliance_rate)
# print(top3_missing)



# folder_2024 = "/home/wahab/Data_Science_Assigment_1_final_draft/tlc_data/tlc_2024"
# folder_2025 = "/home/wahab/Data_Science_Assigment_1_final_draft/tlc_data/tlc_2025"

# congestion_zone_ids = get_congestion_zone_ids()
# comparison = compare_q1_yellow_vs_green(
#     folder_2024,
#     folder_2025,
#     congestion_zone_ids
# )
# print_comparison(comparison)



# print("Phase 3 – Border Effect Analysis (Matplotlib only)")

# print("===============================================")
# change_df, border_ids = calculate_border_dropoff_changes()
# print("\nResults:")
# print(change_df.to_string(index=False))
# generate_choropleth(change_df)




# folder_2024 = "/home/wahab/Data_Science_Assigment_1_final_draft/tlc_data/tlc_2024"
# folder_2025 = "/home/wahab/Data_Science_Assigment_1_final_draft/tlc_data/tlc_2025"
# heatmap_2024, heatmap_2025 = compare_q1_velocity(folder_2024, folder_2025)
# print(heatmap_2024,"\n\n")
# print(heatmap_2025)
# # Print basic stats
# print("\nAverage speed Q1 2024:", heatmap_2024.values.mean().round(1), "mph")
# print("Average speed Q1 2025:", heatmap_2025.values.mean().round(1), "mph")
# print("Overall change:", (heatmap_2025.values.mean() - heatmap_2024.values.mean()).round(1), "mph")
# # Generate beautiful heatmap
# plot_velocity_heatmaps(heatmap_2024, heatmap_2025)



# # Get the congestion zone IDs
# zones = get_congestion_zone_ids()

# df_2025 = run_tip_crowding_out_2025_with_scatter(
#     tlc_2025_folder="tlc_data/tlc_2025",
#     congestion_zone_ids=zones
# )


# phase 4
run_weather_elastisity()

# run_audit_report()