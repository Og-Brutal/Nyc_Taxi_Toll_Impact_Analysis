import os
import pandas as pd
from pathlib import Path
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from Parquet_Loader import tlc_filtered_batches
from Elasticity_Model import run_weather_elastisity

# =====================================================
# CONFIG
# =====================================================
PROJECT_ROOT = Path(__file__).parent
BASE_DIR = str(PROJECT_ROOT / "tlc_data" / "tlc_2025")
REPORT_FILE = "audit_report.pdf"

# =====================================================
# LOAD ALL 2025 FILES
# =====================================================
def load_2025_data():
    rows = []
    for file in os.listdir(BASE_DIR):
        if file.endswith(".parquet"):
            path = os.path.join(BASE_DIR, file)
            for batch in tlc_filtered_batches(path):
                batch = batch.copy()  # avoid SettingWithCopyWarning
                batch["source_file"] = file
                rows.append(batch)

    if rows:
        return pd.concat(rows, ignore_index=True)
    else:
        return pd.DataFrame()  # return empty DataFrame if no files

# =====================================================
# SURCHARGE REVENUE
# =====================================================
def calc_total_surcharge(df):
    return round(df["congestion_surcharge"].sum(), 2)

# =====================================================
# GHOST TRIP VENDOR DETECTION
# =====================================================
def detect_suspicious_vendors(df, top_n=5):
    """
    Detects top N vendors with highest number of trips.
    Returns a DataFrame with columns: vendor_id, total_trips
    """
    if "vendor_id" not in df.columns:
        return pd.DataFrame(columns=["vendor_id", "total_trips"])

    vendor_counts = df.groupby("vendor_id").size().sort_values(ascending=False).head(top_n)
    top_vendors_df = vendor_counts.reset_index()
    top_vendors_df.columns = ["vendor_id", "total_trips"]

    return top_vendors_df

# =====================================================
# RAIN ELASTICITY
# =====================================================
def get_rain_elasticity():
    """
    Uses the Elasticity_Model function to calculate rain elasticity
    for 2025 TLC trips.
    """
    try:
        elasticity_result = run_weather_elastisity()
        r = elasticity_result.get("correlation", None)

        if r is None:
            return "Unavailable (Phase-4 output missing)"
        elif abs(r) < 0.2:
            return "Inelastic (weak weather response)"
        else:
            return "Elastic (strong rain sensitivity)"

    except Exception as e:
        print("⚠️ Error computing rain elasticity:", e)
        return "Unavailable (error during computation)"

# =====================================================
# PDF WRITER
# =====================================================
def create_pdf(total_revenue, elasticity, top_vendors_df):
    styles = getSampleStyleSheet()
    story = []
    doc = SimpleDocTemplate(REPORT_FILE, pagesize=A4)

    # Title
    story.append(Paragraph("<b>TLC Congestion Toll Audit — 2025</b>", styles["Title"]))
    story.append(Spacer(1, 20))

    # Executive Summary
    story.append(Paragraph("<b>Executive Summary</b>", styles["Heading2"]))
    story.append(
        Paragraph(
            f"""
• <b>Total Estimated Congestion Surcharge Revenue:</b> ${total_revenue:,.2f}<br/>
• <b>Rain Elasticity:</b> {elasticity}<br/>
""",
            styles["BodyText"],
        )
    )
    story.append(Spacer(1, 15))

    # Top-5 Suspicious Vendors Table
    story.append(Paragraph("<b>Top-5 Suspicious Vendors (Vendor IDs)</b>", styles["Heading3"]))
    vendor_table = [["vendor_id", "total_trips"]]

    for _, row in top_vendors_df.iterrows():
        vendor_table.append([row["vendor_id"], f"{row['total_trips']:,}"])

    table = Table(vendor_table)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ]
        )
    )
    story.append(table)

    # Policy Recommendation
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>Policy Recommendation</b>", styles["Heading2"]))
    recommendation = (
        "Increase congestion surcharge modestly during rainy days "
        "to offset demand surges, and prioritize audits of vendors "
        "with disproportionate ghost-trip signatures. "
        "Introduce automated GPS anomaly detection in TLC compliance systems."
    )
    story.append(Paragraph(recommendation, styles["BodyText"]))

    # Build PDF
    doc.build(story)
    print(f"\n📄 Audit Report Created → {REPORT_FILE}")

# =====================================================
# MAIN DRIVER
# =====================================================
def run_audit_report():
    print("\n==== GENERATING TLC AUDIT REPORT ====")

    df = load_2025_data()
    if df.empty:
        print("⚠️ No data found for 2025!")
        return

    print("Trips loaded:", len(df))

    revenue = calc_total_surcharge(df)
    print("Total surcharge:", revenue)

    top_vendors_df = detect_suspicious_vendors(df)
    print("Top 5 suspicious vendors:\n", top_vendors_df)

    elasticity_text = get_rain_elasticity()
    print("Rain elasticity:", elasticity_text)

    create_pdf(revenue, elasticity_text, top_vendors_df)
