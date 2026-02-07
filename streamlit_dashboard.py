"""
NYC Congestion Pricing Audit - Interactive Streamlit Dashboard
2025 Analysis Dashboard

Tabs:
1. Border Effect Map - Interactive Folium visualization
2. Velocity Heatmaps - Q1 2024 vs Q1 2025 comparison
3. Tip Economics - Surcharge vs Tip analysis
4. Weather Elasticity - Rain impact on taxi demand
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Import analysis modules
from get_congestion_zone_location_ids import get_congestion_zone_ids
from Hypothesis.Border_Effect import calculate_border_dropoff_changes, generate_interactive_folium_map
from Hypothesis.congestion_velocity import compare_q1_velocity
from Hypothesis.Tip_Crowding_Out_Analysis import aggregate_2025_folder
from Elasticity_Model import fetch_precipitation_2025, compute_daily_trip_counts_2025, merge_weather_trips, compute_rain_elasticity
from Crawler import TLCDownloader
from impute_december_2025_tlc_batches import impute_2025_12_data
from generate_audit_report import run_audit_report

# Page configuration
st.set_page_config(
    page_title="NYC Congestion Pricing Audit 2025",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #1f77b4;
        --secondary-color: #ff7f0e;
        --success-color: #2ca02c;
        --danger-color: #d62728;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.95;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 24px;
        background-color: #f0f2f6;
        border-radius: 8px 8px 0 0;
        font-weight: 600;
        color: #333;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #5a67d8;
        color: white !important;
    }
    
    /* Info boxes */
    .info-box {
        background: #cfe2ff;
        border-left: 4px solid #2196F3;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
        color: #004085;
    }
    
    .warning-box {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
        color: #856404;
    }
    
    .success-box {
        background: #d1e7dd;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
        color: #0f5132;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #666;
        border-top: 1px solid #eee;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def check_data_availability():
    """Check if TLC data directories exist and contain parquet files"""
    data_2024 = project_root / "tlc_data" / "tlc_2024"
    data_2025 = project_root / "tlc_data" / "tlc_2025"
    
    has_2024 = data_2024.exists() and any(f.endswith('.parquet') for f in os.listdir(data_2024))
    has_2025 = data_2025.exists() and any(f.endswith('.parquet') for f in os.listdir(data_2025))
    
    return has_2024, has_2025

def show_data_missing_message(year=None):
    """Display user-friendly message when data is not available"""
    if year:
        message = f"""
        <div class="warning-box">
            <h4>📥 No {year} Data Found</h4>
            <p>The required TLC trip data for {year} is not available.</p>
            <p><strong>👉 Please click the "Download Data" button in the sidebar to download the required data.</strong></p>
            <ol>
                <li>Open the sidebar (← icon in top-left)</li>
                <li>Expand the "🔄 Download TLC Data" section</li>
                <li>Select the year(s) you need</li>
                <li>Click the "📥 Download Data" button</li>
            </ol>
        </div>
        """
    else:
        message = """
        <div class="warning-box">
            <h4>📥 No Data Found</h4>
            <p>The required TLC trip data is not available.</p>
            <p><strong>👉 Please click the "Download Data" button in the sidebar to download the required data.</strong></p>
            <ol>
                <li>Open the sidebar (← icon in top-left)</li>
                <li>Expand the "🔄 Download TLC Data" section</li>
                <li>Select the year(s) you need (2024 and 2025 recommended)</li>
                <li>Click the "📥 Download Data" button</li>
            </ol>
        </div>
        """
    st.markdown(message, unsafe_allow_html=True)

# Caching functions for performance
@st.cache_data(show_spinner=False)
def load_border_effect_data():
    """Load border effect analysis data"""
    try:
        change_df, border_ids = calculate_border_dropoff_changes()
        return change_df, border_ids
    except Exception as e:
        return None, None

@st.cache_data(show_spinner=False)
def load_velocity_data():
    """Load velocity heatmap data"""
    try:
        folder_2024 = str(project_root / "tlc_data" / "tlc_2024")
        folder_2025 = str(project_root / "tlc_data" / "tlc_2025")
        heatmap_2024, heatmap_2025 = compare_q1_velocity(folder_2024, folder_2025)
        return heatmap_2024, heatmap_2025
    except Exception as e:
        return None, None

@st.cache_data(show_spinner=False)
def load_tip_data():
    """Load tip crowding-out analysis data"""
    try:
        zones = get_congestion_zone_ids()
        df_2025 = aggregate_2025_folder(
            tlc_2025_folder="tlc_data/tlc_2025",
            congestion_zone_ids=zones,
            after_date="2025-01-05"
        )
        return df_2025
    except Exception as e:
        return None

@st.cache_data(show_spinner=False)
def load_weather_data():
    """Load weather elasticity data"""
    try:
        zones = get_congestion_zone_ids()
        weather_df = fetch_precipitation_2025()
        trip_df = compute_daily_trip_counts_2025(
            tlc_2025_folder="tlc_data/tlc_2025",
            congestion_zone_ids=zones
        )
        merged = merge_weather_trips(weather_df, trip_df)
        elasticity = compute_rain_elasticity(merged)
        return merged, elasticity
    except Exception as e:
        return None, None

def create_header():
    """Create dashboard header"""
    st.markdown("""
    <div class="main-header">
        <h1>🚕 NYC Congestion Pricing Audit 2025</h1>
        <p>Comprehensive Analysis of Manhattan Congestion Relief Zone Toll Impact</p>
        <p style="font-size: 0.9rem; margin-top: 0.5rem;">
            📅 Analysis Period: January 2025 - December 2025 | 
            🎯 Toll Implementation: January 5, 2025
        </p>
    </div>
    """, unsafe_allow_html=True)

def create_executive_summary():
    """Create executive summary with key metrics"""
    st.markdown("## 📊 Executive Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Analysis Period</div>
            <div class="metric-value">12 Months</div>
            <div style="color: #666; font-size: 0.85rem;">Full Year 2025</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Toll Start Date</div>
            <div class="metric-value">Jan 5</div>
            <div style="color: #666; font-size: 0.85rem;">2025</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Data Sources</div>
            <div class="metric-value">4</div>
            <div style="color: #666; font-size: 0.85rem;">TLC, Weather, GIS, Audit</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Analysis Tabs</div>
            <div class="metric-value">5</div>
            <div style="color: #666; font-size: 0.85rem;">Interactive Dashboards</div>
        </div>
        """, unsafe_allow_html=True)

def tab_border_effect():
    """Tab 1: Border Effect Map"""
    st.markdown("### 🗺️ Border Effect Analysis")
    st.markdown("""
    <div class="info-box">
        <strong>Hypothesis:</strong> Are passengers ending trips just outside the congestion zone to avoid the toll?
        <br><strong>Method:</strong> Compare Q1 2024 vs Q1 2025 drop-off patterns in zones bordering 60th Street.
    </div>
    """, unsafe_allow_html=True)
    
    with st.spinner("Loading border effect data..."):
        change_df, border_ids = load_border_effect_data()
    
    # Check if data was loaded successfully
    if change_df is None or border_ids is None:
        show_data_missing_message()
        return
    
    # Generate interactive map
    map_file = "border_effect_map.html"
    if not os.path.exists(map_file):
        with st.spinner("Generating interactive map..."):
            generate_interactive_folium_map(change_df)
    
    # Display map
    if os.path.exists(map_file):
        with open(map_file, 'r', encoding='utf-8') as f:
            map_html = f.read()
        st.components.v1.html(map_html, height=600, scrolling=True)
    else:
        show_data_missing_message()
    
    # Summary statistics
    st.markdown("#### 📈 Summary Statistics")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Top 5 Zones - Highest Increase**")
        top_increase = change_df.nlargest(5, '% Change')[['LocationID', 'Dropoffs_2024', 'Dropoffs_2025', '% Change']]
        st.dataframe(top_increase, use_container_width=True)
    
    with col2:
        st.markdown("**Top 5 Zones - Highest Decrease**")
        top_decrease = change_df.nsmallest(5, '% Change')[['LocationID', 'Dropoffs_2024', 'Dropoffs_2025', '% Change']]
        st.dataframe(top_decrease, use_container_width=True)
    
    # Overall statistics
    avg_change = change_df['% Change'].mean()
    total_2024 = change_df['Dropoffs_2024'].sum()
    total_2025 = change_df['Dropoffs_2025'].sum()
    
    st.markdown(f"""
    <div class="success-box">
        <strong>Overall Border Zone Impact:</strong><br>
        • Average % Change: <strong>{avg_change:.1f}%</strong><br>
        • Total Drop-offs 2024: <strong>{total_2024:,}</strong><br>
        • Total Drop-offs 2025: <strong>{total_2025:,}</strong><br>
        • Net Change: <strong>{total_2025 - total_2024:+,}</strong>
    </div>
    """, unsafe_allow_html=True)

def tab_velocity_heatmaps():
    """Tab 2: Congestion Velocity Heatmaps"""
    st.markdown("### 🚦 Congestion Velocity Analysis")
    st.markdown("""
    <div class="info-box">
        <strong>Hypothesis:</strong> Did the congestion toll actually speed up traffic inside the zone?
        <br><strong>Method:</strong> Compare average trip speeds by hour and day of week (Q1 2024 vs Q1 2025).
    </div>
    """, unsafe_allow_html=True)
    
    with st.spinner("Loading velocity data..."):
        heatmap_2024, heatmap_2025 = load_velocity_data()
    
    if heatmap_2024 is None or heatmap_2025 is None:
        show_data_missing_message()
        return
    
    # Create side-by-side heatmaps using Plotly
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Q1 2024 - Average Speed (mph)")
        fig_2024 = go.Figure(data=go.Heatmap(
            z=heatmap_2024.values,
            x=list(range(24)),
            y=heatmap_2024.index,
            colorscale='RdYlGn',
            text=heatmap_2024.values.round(1),
            texttemplate='%{text}',
            textfont={"size": 8},
            colorbar=dict(title="Speed (mph)")
        ))
        fig_2024.update_layout(
            xaxis_title="Hour of Day",
            yaxis_title="Day of Week",
            height=400
        )
        st.plotly_chart(fig_2024, use_container_width=True)
    
    with col2:
        st.markdown("#### Q1 2025 - Average Speed (mph)")
        fig_2025 = go.Figure(data=go.Heatmap(
            z=heatmap_2025.values,
            x=list(range(24)),
            y=heatmap_2025.index,
            colorscale='RdYlGn',
            text=heatmap_2025.values.round(1),
            texttemplate='%{text}',
            textfont={"size": 8},
            colorbar=dict(title="Speed (mph)")
        ))
        fig_2025.update_layout(
            xaxis_title="Hour of Day",
            yaxis_title="Day of Week",
            height=400
        )
        st.plotly_chart(fig_2025, use_container_width=True)
    
    # Calculate and display change
    st.markdown("#### 📊 Speed Change Analysis")
    speed_change = heatmap_2025 - heatmap_2024
    
    fig_change = go.Figure(data=go.Heatmap(
        z=speed_change.values,
        x=list(range(24)),
        y=speed_change.index,
        colorscale='RdYlGn',
        text=speed_change.values.round(1),
        texttemplate='%{text}',
        textfont={"size": 8},
        colorbar=dict(title="Speed Change (mph)"),
        zmid=0
    ))
    fig_change.update_layout(
        title="Speed Change: Q1 2025 vs Q1 2024 (Positive = Faster)",
        xaxis_title="Hour of Day",
        yaxis_title="Day of Week",
        height=400
    )
    st.plotly_chart(fig_change, use_container_width=True)
    
    # Summary metrics
    avg_2024 = heatmap_2024.values.mean()
    avg_2025 = heatmap_2025.values.mean()
    avg_change = avg_2025 - avg_2024
    pct_change = (avg_change / avg_2024) * 100
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Avg Speed 2024", f"{avg_2024:.1f} mph")
    with col2:
        st.metric("Avg Speed 2025", f"{avg_2025:.1f} mph")
    with col3:
        st.metric("Speed Change", f"{avg_change:+.1f} mph", f"{pct_change:+.1f}%")
    with col4:
        verdict = "✅ Faster" if avg_change > 0 else "⚠️ Slower"
        st.metric("Verdict", verdict)

def tab_tip_economics():
    """Tab 3: Tip Crowding-Out Analysis"""
    st.markdown("### 💰 Tip Economics Analysis")
    st.markdown("""
    <div class="info-box">
        <strong>Hypothesis:</strong> Higher congestion tolls reduce disposable income passengers leave for drivers.
        <br><strong>Method:</strong> Analyze correlation between average surcharge and tip percentage (2025 data).
    </div>
    """, unsafe_allow_html=True)
    
    with st.spinner("Loading tip analysis data..."):
        df_2025 = load_tip_data()
    
    if df_2025 is None or df_2025.empty:
        show_data_missing_message(year=2025)
        return
    
    df_2025 = df_2025.sort_index()
    df_2025['month_str'] = df_2025.index.astype(str)
    
    # Dual-axis chart using Plotly
    st.markdown("#### 📊 Monthly Trend: Surcharge vs Tip Percentage")
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add surcharge bars
    fig.add_trace(
        go.Bar(
            x=df_2025['month_str'],
            y=df_2025['avg_surcharge'],
            name="Avg Surcharge ($)",
            marker_color='#667eea',
            opacity=0.7
        ),
        secondary_y=False
    )
    
    # Add tip percentage line
    fig.add_trace(
        go.Scatter(
            x=df_2025['month_str'],
            y=df_2025['avg_tip_percent'],
            name="Avg Tip %",
            mode='lines+markers',
            marker=dict(size=10, color='#ff7f0e'),
            line=dict(width=3, color='#ff7f0e')
        ),
        secondary_y=True
    )
    
    fig.update_xaxes(title_text="Month")
    fig.update_yaxes(title_text="Avg Surcharge ($)", secondary_y=False)
    fig.update_yaxes(title_text="Avg Tip (%)", secondary_y=True)
    fig.update_layout(
        title="Congestion Surcharge vs Driver Tips (2025)",
        height=500,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Scatter plot with regression
    st.markdown("#### 🔍 Correlation Analysis")
    
    from scipy.stats import linregress
    slope, intercept, r_value, p_value, std_err = linregress(
        df_2025['avg_surcharge'],
        df_2025['avg_tip_percent']
    )
    
    fig_scatter = go.Figure()
    
    # Scatter points
    fig_scatter.add_trace(go.Scatter(
        x=df_2025['avg_surcharge'],
        y=df_2025['avg_tip_percent'],
        mode='markers',
        marker=dict(size=12, color='#667eea'),
        name='Monthly Data',
        text=df_2025['month_str'],
        hovertemplate='<b>%{text}</b><br>Surcharge: $%{x:.2f}<br>Tip: %{y:.2f}%<extra></extra>'
    ))
    
    # Regression line
    x_range = np.linspace(df_2025['avg_surcharge'].min(), df_2025['avg_surcharge'].max(), 100)
    y_pred = intercept + slope * x_range
    
    fig_scatter.add_trace(go.Scatter(
        x=x_range,
        y=y_pred,
        mode='lines',
        line=dict(color='red', width=2, dash='dash'),
        name=f'Trend Line (r={r_value:.3f})'
    ))
    
    fig_scatter.update_layout(
        title="Surcharge vs Tip Percentage - Correlation Analysis",
        xaxis_title="Average Congestion Surcharge ($)",
        yaxis_title="Average Tip (%)",
        height=500
    )
    
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Correlation (r)", f"{r_value:.3f}")
    with col2:
        st.metric("P-value", f"{p_value:.4f}")
    with col3:
        significance = "✅ Significant" if p_value < 0.05 else "⚠️ Not Significant"
        st.metric("Statistical Significance", significance)
    
    interpretation = "negative" if r_value < 0 else "positive"
    strength = "strong" if abs(r_value) > 0.7 else "moderate" if abs(r_value) > 0.4 else "weak"
    
    st.markdown(f"""
    <div class="{'warning-box' if r_value < 0 else 'success-box'}">
        <strong>Interpretation:</strong> There is a <strong>{strength} {interpretation}</strong> correlation 
        between congestion surcharge and tip percentage (r = {r_value:.3f}).
        {'This suggests the "crowding out" effect may be present.' if r_value < 0 else 'This suggests tips are not negatively impacted by the surcharge.'}
    </div>
    """, unsafe_allow_html=True)

def tab_weather_elasticity():
    """Tab 4: Weather Elasticity Analysis"""
    st.markdown("### 🌧️ Rain Tax Analysis")
    st.markdown("""
    <div class="info-box">
        <strong>Hypothesis:</strong> Rainfall increases taxi demand (people avoid walking/biking).
        <br><strong>Method:</strong> Correlate daily precipitation with taxi trip counts in the congestion zone.
    </div>
    """, unsafe_allow_html=True)
    
    with st.spinner("Loading weather elasticity data..."):
        merged, elasticity = load_weather_data()
    
    if merged is None or elasticity is None or merged.empty:
        show_data_missing_message(year=2025)
        return
    
    # Find wettest month
    merged['month'] = pd.to_datetime(merged['date']).dt.to_period('M')
    wettest_month = merged.groupby('month')['precip_mm'].sum().idxmax()
    wet_df = merged[merged['month'] == wettest_month].copy()
    
    # Overall scatter plot
    st.markdown("#### 📊 Full Year 2025: Precipitation vs Trip Count")
    
    fig_full = go.Figure()
    
    fig_full.add_trace(go.Scatter(
        x=merged['precip_mm'],
        y=merged['trip_count'],
        mode='markers',
        marker=dict(
            size=8,
            color=merged['precip_mm'],
            colorscale='Blues',
            showscale=True,
            colorbar=dict(title="Precip (mm)")
        ),
        text=merged['date'].astype(str),
        hovertemplate='<b>%{text}</b><br>Precipitation: %{x:.1f} mm<br>Trips: %{y:,}<extra></extra>'
    ))
    
    # Add regression line
    from scipy.stats import linregress
    slope_full, intercept_full, r_full, p_full, _ = linregress(merged['precip_mm'], merged['trip_count'])
    x_range = np.linspace(0, merged['precip_mm'].max(), 100)
    y_pred = intercept_full + slope_full * x_range
    
    fig_full.add_trace(go.Scatter(
        x=x_range,
        y=y_pred,
        mode='lines',
        line=dict(color='red', width=2, dash='dash'),
        name=f'Trend (r={r_full:.3f})'
    ))
    
    fig_full.update_layout(
        xaxis_title="Daily Precipitation (mm)",
        yaxis_title="Daily Trip Count",
        height=500,
        showlegend=True
    )
    
    st.plotly_chart(fig_full, use_container_width=True)
    
    # Wettest month analysis
    st.markdown(f"#### 🌧️ Wettest Month Analysis: {wettest_month}")
    
    fig_wet = go.Figure()
    
    fig_wet.add_trace(go.Scatter(
        x=wet_df['precip_mm'],
        y=wet_df['trip_count'],
        mode='markers',
        marker=dict(size=12, color='#667eea'),
        text=pd.to_datetime(wet_df['date']).dt.strftime('%Y-%m-%d'),
        hovertemplate='<b>%{text}</b><br>Precipitation: %{x:.1f} mm<br>Trips: %{y:,}<extra></extra>'
    ))
    
    # Regression for wettest month
    slope_wet, intercept_wet, r_wet, p_wet, _ = linregress(wet_df['precip_mm'], wet_df['trip_count'])
    x_wet = np.linspace(0, wet_df['precip_mm'].max(), 100)
    y_wet = intercept_wet + slope_wet * x_wet
    
    fig_wet.add_trace(go.Scatter(
        x=x_wet,
        y=y_wet,
        mode='lines',
        line=dict(color='red', width=2),
        name=f'Fit Line (r={r_wet:.3f})'
    ))
    
    fig_wet.update_layout(
        title=f"Wettest Month ({wettest_month}): Precipitation vs Trips",
        xaxis_title="Daily Precipitation (mm)",
        yaxis_title="Daily Trip Count",
        height=500
    )
    
    st.plotly_chart(fig_wet, use_container_width=True)
    
    # Elasticity metrics
    st.markdown("#### 📈 Elasticity Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Correlation (r)", f"{elasticity['correlation']:.3f}")
    with col2:
        st.metric("Slope (trips/mm)", f"{elasticity['slope']:.1f}")
    with col3:
        st.metric("P-value", f"{elasticity['p_value']:.5f}")
    with col4:
        elasticity_type = "Inelastic" if abs(elasticity['correlation']) < 0.3 else "Elastic"
        st.metric("Demand Type", elasticity_type)
    
    # Interpretation
    if elasticity['correlation'] > 0:
        interpretation = "positive"
        meaning = "Taxi demand <strong>increases</strong> with rainfall, confirming the 'Rain Tax' effect."
    else:
        interpretation = "negative"
        meaning = "Taxi demand <strong>decreases</strong> with rainfall (unexpected result)."
    
    st.markdown(f"""
    <div class="{'success-box' if elasticity['correlation'] > 0 else 'warning-box'}">
        <strong>Rain Elasticity Interpretation:</strong><br>
        • Correlation is <strong>{interpretation}</strong> (r = {elasticity['correlation']:.3f})<br>
        • {meaning}<br>
        • For every 1mm of rain, trip count changes by approximately <strong>{elasticity['slope']:.0f} trips</strong><br>
        • Statistical significance: <strong>{'Yes (p < 0.05)' if elasticity['p_value'] < 0.05 else 'No (p ≥ 0.05)'}</strong>
    </div>
    """, unsafe_allow_html=True)

def tab_audit_report():
    """Tab 5: Audit Report Generation"""
    st.markdown("### 📄 Audit Report")
    st.markdown("""
    <div class="info-box">
        <strong>Purpose:</strong> Generate comprehensive PDF audit report with key findings.
        <br><strong>Includes:</strong> Total surcharge revenue, rain elasticity score, top suspicious vendors, and policy recommendations.
    </div>
    """, unsafe_allow_html=True)
    
    # Report generation section
    st.markdown("#### 🔧 Generate Report")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        The audit report includes:
        - **Total Estimated 2025 Surcharge Revenue**
        - **Rain Elasticity Score** (elastic vs inelastic demand)
        - **Top 5 Suspicious Vendors** (based on trip volume)
        - **Policy Recommendations** (data-backed suggestions)
        """)
    
    with col2:
        if st.button("📊 Generate PDF Report", type="primary", use_container_width=True):
            with st.spinner("Generating audit report..."):
                try:
                    run_audit_report()
                    st.success("✅ Report generated successfully!")
                except Exception as e:
                    st.error(f"❌ Error generating report: {str(e)}")
    
    # Check if report exists and display download button
    report_file = "audit_report.pdf"
    if os.path.exists(report_file):
        st.markdown("#### 📥 Download Report")
        
        with open(report_file, "rb") as f:
            pdf_data = f.read()
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.download_button(
                label="⬇️ Download Audit Report PDF",
                data=pdf_data,
                file_name="NYC_Congestion_Audit_Report_2025.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
        st.markdown("""
        <div class="success-box">
            <strong>Report Ready!</strong> The audit report has been generated and is available for download.
            This report can be included in your assignment submission.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="warning-box">
            <strong>No Report Found:</strong> Click the "Generate PDF Report" button above to create the audit report.
        </div>
        """, unsafe_allow_html=True)
    
    # Report preview section
    st.markdown("#### 👁️ Report Contents Preview")
    
    with st.expander("📋 Executive Summary"):
        st.markdown("""
        - Total Estimated Congestion Surcharge Revenue
        - Rain Elasticity Classification (Elastic/Inelastic)
        - Top 5 Suspicious Vendors by trip volume
        """)
    
    with st.expander("🚨 Top Suspicious Vendors"):
        st.markdown("""
        Table showing vendor IDs with highest trip counts, which may indicate:
        - High-volume legitimate operators
        - Potential data quality issues
        - Candidates for GPS fraud audits
        """)
    
    with st.expander("💡 Policy Recommendations"):
        st.markdown("""
        Data-backed suggestions including:
        - Dynamic pricing during high-demand periods (rain)
        - Vendor audit prioritization
        - GPS anomaly detection systems
        - Toll optimization strategies
        """)


def main():
    """Main dashboard application"""
    
    # Sidebar
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/NYC_Logo_Wolff_Olins.svg/1200px-NYC_Logo_Wolff_Olins.svg.png", width=150)
        st.markdown("---")
        
        # Data Crawler Section
        st.markdown("### 📥 Data Management")
        with st.expander("🔄 Download TLC Data"):
            st.markdown("Download fresh data from NYC TLC:")
            
            years_to_download = st.multiselect(
                "Select Years",
                [2023, 2024, 2025],
                default=[2024, 2025]
            )
            
            if st.button("📥 Download Data", use_container_width=True):
                with st.spinner("Downloading TLC data..."):
                    try:
                        downloader = TLCDownloader(base_download_dir="tlc_data")
                        folder = downloader.get_folder("taxi_zone_lookup")
                        
                        for year in years_to_download:
                            st.info(f"Downloading {year} data...")
                            downloader.download_year(year, taxi_types=("yellow", "green"))
                        
                        downloader.download_file(
                            "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv",
                            folder
                        )
                        
                        # Impute December 2025 if needed
                        if 2025 in years_to_download:
                            st.info("Imputing December 2025 data...")
                            impute_2025_12_data()
                        
                        st.success("✅ Data downloaded successfully!")
                        st.cache_data.clear()  # Clear cache to reload new data
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        
        st.markdown("---")
        st.markdown("### 📋 Navigation")
        st.markdown("""
        Use the tabs to explore different aspects of the congestion pricing impact:
        
        - **🗺️ Border Effect**: Zone-level drop-off changes
        - **🚦 Velocity**: Traffic speed analysis
        - **💰 Tip Economics**: Driver income impact
        - **🌧️ Weather**: Rain elasticity
        - **📄 Audit Report**: PDF report generation
        """)
        
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.markdown("""
        **Data Sources:**
        - NYC TLC Trip Records
        - Open-Meteo Weather API
        - NYC Taxi Zone Shapefiles
        
        **Analysis Period:**
        - January 2025 - December 2025
        
        **Toll Implementation:**
        - January 5, 2025
        """)
        
        st.markdown("---")
        st.markdown("### 🔗 Resources")
        st.markdown("""
        - [GitHub Repository](https://github.com/Og-Brutal/Nyc_Taxi_Toll_Impact_Analysis.git)
        - [LinkedIn Post](https://www.linkedin.com/posts/abdul-wahab-09b364388_datascience-python-streamlit-activity-7425788624950001690-18Ls?utm_source=share&utm_medium=member_desktop)
        - [Medium Blog](https://medium.com/@ogbrutal2825/nyc-congestion-pricing-audit-a-data-driven-analysis-dashboard-1538222375e9)
        """)
    
    # Main content
    create_header()
    create_executive_summary()
    
    st.markdown("---")
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🗺️ Border Effect Map",
        "🚦 Velocity Heatmaps",
        "💰 Tip Economics",
        "🌧️ Weather Elasticity",
        "📄 Audit Report"
    ])
    
    with tab1:
        tab_border_effect()
    
    with tab2:
        tab_velocity_heatmaps()
    
    with tab3:
        tab_tip_economics()
    
    with tab4:
        tab_weather_elasticity()
    
    with tab5:
        tab_audit_report()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div class="footer">
        <p>NYC Congestion Pricing Audit Dashboard | Data Science Assignment 2025</p>
        <p style="font-size: 0.85rem; color: #999;">
            Built with Streamlit | Data from NYC TLC & Open-Meteo
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
