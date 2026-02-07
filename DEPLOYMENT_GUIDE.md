# NYC Congestion Pricing Audit Dashboard - Deployment Guide

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd /home/wahab/Data_Science_Assigment_1_final_draft
pip install -r requirements.txt
```

### 2. Run Dashboard Locally

```bash
streamlit run streamlit_dashboard.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`

---

## 📋 Prerequisites

- Python 3.8 or higher
- All TLC data files in `tlc_data/` directory
- Weather data CSV file
- Taxi zone shapefiles

---

## 🌐 Deploy to Streamlit Cloud

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Add NYC Congestion Pricing Audit Dashboard"
git remote add origin <your-github-repo-url>
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Set main file path: `streamlit_dashboard.py`
6. Click "Deploy"

### Step 3: Configure Settings

- **Python version**: 3.9+
- **Requirements file**: `requirements.txt`
- **Secrets**: None required (all data is local)

---

## 📊 Dashboard Features

### Tab 1: Border Effect Map 🗺️
- **Interactive Folium map** with clickable zones
- Color-coded by % change in drop-offs
- Tooltips with detailed statistics
- Top 5 zones analysis

### Tab 2: Velocity Heatmaps 🚦
- Side-by-side Q1 2024 vs Q1 2025 comparison
- Hour-by-hour, day-by-day speed analysis
- Speed change visualization
- Summary metrics

### Tab 3: Tip Economics 💰
- Dual-axis chart: Surcharge vs Tip %
- Scatter plot with regression analysis
- Correlation statistics
- Monthly trend analysis

### Tab 4: Weather Elasticity 🌧️
- Daily precipitation vs trip count
- Wettest month deep-dive
- Elasticity coefficient calculation
- Statistical significance testing

---

## 🎨 Customization

### Modify Color Scheme

Edit the CSS in `streamlit_dashboard.py`:

```python
st.markdown("""
<style>
    /* Change primary gradient */
    background: linear-gradient(135deg, #YOUR_COLOR_1 0%, #YOUR_COLOR_2 100%);
</style>
""", unsafe_allow_html=True)
```

### Add New Tabs

1. Create new function: `def tab_your_analysis():`
2. Add tab in main: `tab5 = st.tabs(["Your Tab"])`
3. Call function: `with tab5: tab_your_analysis()`

---

## 🐛 Troubleshooting

### Issue: "Module not found"
**Solution**: Install missing package
```bash
pip install <package-name>
```

### Issue: "Data files not found"
**Solution**: Ensure all data is in correct directories:
- TLC data: `tlc_data/tlc_2024/` and `tlc_data/tlc_2025/`
- Weather: `weather_2025_central_park.csv`
- Shapefiles: `taxi_zones.zip`

### Issue: "Map not displaying"
**Solution**: Regenerate the map
```python
from Hypothesis.Border_Effect import calculate_border_dropoff_changes, generate_interactive_folium_map
change_df, _ = calculate_border_dropoff_changes()
generate_interactive_folium_map(change_df)
```

### Issue: "Slow loading"
**Solution**: Streamlit caches data automatically. First load may be slow, subsequent loads will be fast.

---

## 📦 File Structure

```
Data_Science_Assigment_1_final_draft/
├── streamlit_dashboard.py          # Main dashboard application
├── requirements.txt                # Python dependencies
├── Hypothesis/
│   ├── Border_Effect.py           # Enhanced with Folium map
│   ├── congestion_velocity.py
│   ├── Tip_Crowding_Out_Analysis.py
│   └── VIisualizing_Heat_Maps.py
├── Elasticity_Model.py
├── get_congestion_zone_location_ids.py
├── Parquet_Loader.py
├── tlc_data/                      # TLC trip data
├── weather_2025_central_park.csv
└── taxi_zones.zip
```

---

## 🔗 Sharing Your Dashboard

### Option 1: Streamlit Cloud (Recommended)
- Free hosting
- Automatic updates from GitHub
- Shareable public URL
- Example: `https://your-username-nyc-audit.streamlit.app`

### Option 2: Local Sharing
```bash
# Run with custom port
streamlit run streamlit_dashboard.py --server.port 8080

# Share via ngrok (temporary public URL)
ngrok http 8501
```

### Option 3: Export to Static HTML
Individual visualizations can be exported:
- Border Effect Map: Already saved as `border_effect_map.html`
- Other plots: Use Plotly's `fig.write_html("filename.html")`

---

## 📝 Assignment Submission Checklist

- [ ] Dashboard running locally
- [ ] All 4 tabs functioning correctly
- [ ] Interactive map displays properly
- [ ] Deploy to Streamlit Cloud
- [ ] Get shareable link
- [ ] Test link in incognito mode
- [ ] Add link to submission document
- [ ] Create LinkedIn post with dashboard link
- [ ] Write Medium blog with screenshots
- [ ] Push code to GitHub repository

---

## 💡 Tips for Best Results

1. **Data Preparation**: Ensure all analysis has been run at least once to generate cached data
2. **Performance**: First load takes time; subsequent loads are cached
3. **Mobile**: Dashboard is responsive and works on mobile devices
4. **Screenshots**: Use browser's screenshot tool to capture visualizations for reports
5. **Updates**: Any changes to code will auto-reload in development mode

---

## 📞 Support

For issues or questions:
- Check Streamlit docs: [docs.streamlit.io](https://docs.streamlit.io)
- Folium docs: [python-visualization.github.io/folium](https://python-visualization.github.io/folium/)
- Plotly docs: [plotly.com/python](https://plotly.com/python/)

---

**Good luck with your submission! 🎓**
