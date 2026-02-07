# NYC Congestion Pricing Audit - Interactive Dashboard

## 🎯 Project Overview

This is a comprehensive Streamlit dashboard for analyzing the impact of NYC's Manhattan Congestion Relief Zone Toll implemented on January 5, 2025. The dashboard provides interactive visualizations and statistical analysis across four key areas.

## 📊 Dashboard Features

### 1. 🗺️ Border Effect Map
- **Interactive Folium map** showing zones bordering the congestion zone
- Color-coded visualization of % change in drop-offs (Q1 2024 vs Q1 2025)
- Clickable zones with detailed tooltips
- Top 5 zones analysis (highest increase/decrease)

### 2. 🚦 Velocity Heatmaps
- Side-by-side comparison of Q1 2024 vs Q1 2025 traffic speeds
- Hour-by-hour and day-by-day breakdown
- Speed change visualization
- Statistical summary metrics

### 3. 💰 Tip Economics Analysis
- Dual-axis chart showing surcharge vs tip percentage trends
- Scatter plot with regression analysis
- Correlation coefficient and statistical significance
- Monthly trend analysis for 2025

### 4. 🌧️ Weather Elasticity
- Daily precipitation vs taxi trip count analysis
- Wettest month deep-dive
- Rain elasticity coefficient calculation
- Full-year and monthly correlation analysis

## 🚀 Quick Start

### Option 1: Using Virtual Environment (Recommended)

```bash
# Navigate to project directory
cd /home/wahab/Data_Science_Assigment_1_final_draft

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run dashboard
streamlit run streamlit_dashboard.py
```

### Option 2: Using System Python (if allowed)

```bash
cd /home/wahab/Data_Science_Assigment_1_final_draft
pip install -r requirements.txt --user
streamlit run streamlit_dashboard.py
```

### Option 3: Using pipx

```bash
pipx install streamlit
# Then install other dependencies in a venv as shown in Option 1
```

## 📦 Dependencies

All required packages are listed in `requirements.txt`:
- streamlit (dashboard framework)
- folium (interactive maps)
- plotly (interactive charts)
- pandas, numpy (data processing)
- geopandas (geospatial analysis)
- scipy (statistical analysis)
- And more...

## 📁 Project Structure

```
Data_Science_Assigment_1_final_draft/
├── streamlit_dashboard.py              # Main dashboard application ⭐
├── requirements.txt                    # Python dependencies
├── DEPLOYMENT_GUIDE.md                 # Detailed deployment instructions
├── README.md                           # This file
│
├── Hypothesis/                         # Analysis modules
│   ├── Border_Effect.py               # Enhanced with interactive map
│   ├── congestion_velocity.py
│   ├── Tip_Crowding_Out_Analysis.py
│   └── VIisualizing_Heat_Maps.py
│
├── Elasticity_Model.py                # Weather elasticity analysis
├── get_congestion_zone_location_ids.py
├── Parquet_Loader.py                  # Big data batch processing
├── Leakage_Audit.py
├── Yellow_vs_Green_Decline.py
│
├── tlc_data/                          # TLC trip data (not in repo)
│   ├── tlc_2024/
│   └── tlc_2025/
│
├── weather_2025_central_park.csv      # Weather data
├── taxi_zones.zip                     # NYC taxi zone shapefiles
└── audit_report.pdf                   # Generated report
```

## 🎨 Dashboard Design

The dashboard features:
- **Professional gradient theme** (purple/blue)
- **Responsive layout** that works on all screen sizes
- **Interactive visualizations** using Plotly and Folium
- **Cached data loading** for optimal performance
- **Executive summary** with key metrics
- **Sidebar navigation** with project information

## 🌐 Deployment Options

### Streamlit Cloud (Recommended for Sharing)

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Deploy with one click
5. Get shareable public URL

See `DEPLOYMENT_GUIDE.md` for detailed instructions.

### Local Network Sharing

```bash
# Run on custom port
streamlit run streamlit_dashboard.py --server.port 8080

# Share via ngrok (temporary public URL)
ngrok http 8501
```

## 📝 Usage Instructions

1. **First Time Setup**: Run all analysis scripts to generate data files
2. **Launch Dashboard**: Use one of the quick start methods above
3. **Navigate Tabs**: Use the tab interface to explore different analyses
4. **Interact**: Hover over charts, click map zones, view tooltips
5. **Export**: Take screenshots or export individual visualizations

## 🔍 Data Requirements

Before running the dashboard, ensure you have:
- ✅ TLC trip data for 2024 and 2025 in `tlc_data/` directory
- ✅ Weather data CSV file
- ✅ Taxi zone shapefiles (automatically downloaded if missing)
- ✅ All analysis modules have been run at least once

## 🐛 Troubleshooting

### Dashboard won't start
- Ensure all dependencies are installed
- Check Python version (3.8+)
- Verify virtual environment is activated

### Data not loading
- Run individual analysis scripts first
- Check file paths in dashboard code
- Ensure data files exist in correct locations

### Map not displaying
- Install folium: `pip install folium streamlit-folium`
- Regenerate map using Border_Effect.py
- Check browser console for errors

## 📊 Assignment Submission

This dashboard fulfills the requirement:
> "3. Interactive Streamlit Dashboard
> • Tab 1: The Map. Interactive Folium/PyDeck map of the "Border Effect."
> • Tab 2: The Flow. Side-by-side "Velocity Heatmaps" (Before vs. After).
> • Tab 3: The Economics. Tip Percentage vs. Surcharge analysis.
> • Tab 4: The Weather. Rain Elasticity scatter plots."

### Submission Checklist
- [ ] Dashboard running locally
- [ ] All 4 tabs working correctly
- [ ] Deploy to Streamlit Cloud
- [ ] Get shareable link
- [ ] Add to submission ZIP
- [ ] Include in LinkedIn post
- [ ] Feature in Medium blog
- [ ] Push to GitHub

## 🔗 Links

- **GitHub Repository**: [Add your link]
- **Live Dashboard**: [Add Streamlit Cloud link]
- **Medium Blog**: [Add your link]
- **LinkedIn Post**: [Add your link]

## 👨‍💻 Technical Details

- **Framework**: Streamlit 1.28+
- **Visualization**: Plotly, Folium, Matplotlib, Seaborn
- **Data Processing**: Pandas, GeoPandas, NumPy
- **Statistical Analysis**: SciPy
- **Geospatial**: Shapely, Fiona

## 📄 License

Academic project for Data Science Assignment 2025

---

**Built with ❤️ for NYC Congestion Pricing Analysis**

For detailed deployment instructions, see `DEPLOYMENT_GUIDE.md`
