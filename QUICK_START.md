# 🚀 Quick Start Guide - NYC Congestion Pricing Dashboard

## Installation (Choose One Method)

### Method 1: Automated Script (Recommended)
```bash
cd /home/wahab/Data_Science_Assigment_1_final_draft
./install_dashboard.sh
source venv/bin/activate
streamlit run streamlit_dashboard.py
```

### Method 2: Manual Setup
```bash
cd /home/wahab/Data_Science_Assigment_1_final_draft
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_dashboard.py
```

## Dashboard URL
Once running, open: **http://localhost:8501**

## 📋 What You Get

### Tab 1: 🗺️ Border Effect Map
- Interactive Folium map
- Clickable zones with tooltips
- Color-coded % change visualization

### Tab 2: 🚦 Velocity Heatmaps
- Q1 2024 vs Q1 2025 comparison
- Hour-by-hour speed analysis
- Speed change visualization

### Tab 3: 💰 Tip Economics
- Surcharge vs Tip % trends
- Scatter plot with regression
- Correlation analysis

### Tab 4: 🌧️ Weather Elasticity
- Precipitation vs trips
- Wettest month analysis
- Elasticity metrics

### Tab 5: 📄 Audit Report (NEW!)
- Generate PDF audit report
- Download report button
- Executive summary with key findings
- Top suspicious vendors
- Policy recommendations

### 📥 Data Crawler (NEW!)
- Download fresh TLC data from sidebar
- Select years: 2023, 2024, 2025
- Automatic December 2025 imputation
- Cache refresh after download

## 🌐 Deploy to Streamlit Cloud

```bash
# 1. Push to GitHub
git init
git add .
git commit -m "NYC Congestion Pricing Dashboard"
git remote add origin <your-repo-url>
git push -u origin main

# 2. Go to share.streamlit.io
# 3. Connect GitHub repo
# 4. Deploy streamlit_dashboard.py
# 5. Get public URL
```

## 📦 Files Created

- ✅ `streamlit_dashboard.py` - Main dashboard (24KB)
- ✅ `Hypothesis/Border_Effect.py` - Enhanced with Folium map
- ✅ `requirements.txt` - Dependencies
- ✅ `README.md` - Full documentation
- ✅ `DEPLOYMENT_GUIDE.md` - Detailed guide
- ✅ `install_dashboard.sh` - Auto installer
- ✅ `QUICK_START.md` - This file

## 🎯 Assignment Submission

### Include in ZIP:
- All Python files
- `requirements.txt`
- `README.md`
- `DEPLOYMENT_GUIDE.md`
- `audit_report.pdf`

### Links to Submit:
- [ ] GitHub repo URL
- [ ] Streamlit Cloud URL (live dashboard)
- [ ] Medium blog URL
- [ ] LinkedIn post URL

## ⚡ Troubleshooting

**Dashboard won't start?**
```bash
# Check if in virtual environment
which python  # Should show venv path

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Map not showing?**
```bash
# Regenerate map
python3 -c "from Hypothesis.Border_Effect import *; df, _ = calculate_border_dropoff_changes(); generate_interactive_folium_map(df)"
```

**Missing data?**
- Ensure TLC data is in `tlc_data/tlc_2024/` and `tlc_data/tlc_2025/`
- Check `weather_2025_central_park.csv` exists
- Verify `taxi_zones.zip` is present

## 📞 Need Help?

See full documentation:
- `README.md` - Overview
- `DEPLOYMENT_GUIDE.md` - Detailed instructions
- `walkthrough.md` - Technical details

---

**Ready to deploy! 🎉**
