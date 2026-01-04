import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

from src.pipeline.predict_pipeline import PredictPipeline
from src.analytics.kpi import ChurnKPI

# ===== Page Configuration =====
st.set_page_config(
    page_title="Customer Churn Prediction Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"Get Help": None, "Report a bug": None, "About": None}
)

# ===== Custom CSS Styling - Pure Dark Theme with 3D Effects =====
st.markdown("""
    <style>
    /* Root variables */
    :root {
        --primary: #6366f1;
        --primary-light: #818cf8;
        --primary-dark: #4f46e5;
        --danger: #ef4444;
        --danger-light: #f87171;
        --success: #10b981;
        --warning: #f59e0b;
        --info: #3b82f6;
        --dark-bg: #000000;
        --dark-card: #1a1a1a;
        --dark-border: #2a2a2a;
        --text-primary: #f1f5f9;
        --text-secondary: #cbd5e1;
        --text-tertiary: #94a3b8;
    }
    
    /* Hide default streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Pure black background */
    body, .main, .stApp {
        background: linear-gradient(135deg, #000000 0%, #0a0a0a 50%, #000000 100%) !important;
        color: var(--text-primary) !important;
        font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--dark-bg);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--dark-border);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary-light);
    }
    
    /* Custom metric cards with 3D depth */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1a1a1a 0%, #000000 100%);
        padding: 24px;
        border-radius: 16px;
        border: 1px solid var(--dark-border);
        box-shadow: 
            0 20px 40px rgba(0, 0, 0, 0.9),
            0 0 100px rgba(99, 102, 241, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
    }
    
    [data-testid="metric-container"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.3), transparent);
        transition: left 0.5s;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-8px) translateZ(50px);
        box-shadow: 
            0 40px 80px rgba(99, 102, 241, 0.3),
            0 0 150px rgba(99, 102, 241, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        border-color: var(--primary);
    }
    
    [data-testid="metric-container"]:hover::before {
        left: 100%;
    }
    
    /* Dataframe styling */
    [data-testid="stDataFrame"] {
        border-radius: 16px;
        overflow: hidden;
        background: linear-gradient(135deg, #1a1a1a 0%, #000000 100%);
        border: 1px solid var(--dark-border);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.9), 0 0 60px rgba(99, 102, 241, 0.1);
    }
    
    /* Button styling with 3D effect */
    .stButton>button {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 14px 28px;
        font-weight: 700;
        font-size: 0.95rem;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 
            0 10px 30px rgba(99, 102, 241, 0.4),
            0 0 60px rgba(99, 102, 241, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .stButton>button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        transition: left 0.5s;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px) translateZ(20px);
        box-shadow: 
            0 20px 50px rgba(99, 102, 241, 0.6),
            0 0 100px rgba(99, 102, 241, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.3);
    }
    
    .stButton>button:hover::before {
        left: 100%;
    }
    
    .stButton>button:active {
        transform: translateY(-1px);
    }
    
    /* Download button */
    .stDownloadButton>button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        box-shadow: 
            0 10px 30px rgba(16, 185, 129, 0.4),
            0 0 60px rgba(16, 185, 129, 0.2);
    }
    
    .stDownloadButton>button:hover {
        box-shadow: 
            0 20px 50px rgba(16, 185, 129, 0.6),
            0 0 100px rgba(16, 185, 129, 0.3);
    }
    
    /* File uploader styling */
    .stFileUploader {
        border-radius: 16px;
        overflow: hidden;
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 2px dashed var(--primary) !important;
        box-shadow: 0 0 50px rgba(99, 102, 241, 0.2);
    }
    
    /* Header styling with gradient and glow */
    h1 {
        color: var(--text-primary) !important;
        font-size: 3.2rem !important;
        font-weight: 900 !important;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #6366f1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 10px !important;
        text-shadow: 0 0 30px rgba(99, 102, 241, 0.3);
        filter: drop-shadow(0 0 20px rgba(99, 102, 241, 0.2));
    }
    
    h2 {
        color: var(--text-primary) !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
        margin-top: 40px !important;
        margin-bottom: 20px !important;
        padding-bottom: 15px;
        border-bottom: 3px solid var(--primary);
        display: inline-block;
        background: linear-gradient(135deg, #f1f5f9 0%, #cbd5e1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    h3 {
        color: var(--text-primary) !important;
        font-weight: 700 !important;
    }
    
    /* Info/Success/Warning boxes */
    .stInfo {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(99, 102, 241, 0.15) 100%) !important;
        border-left: 4px solid var(--info) !important;
        border-radius: 12px !important;
        padding: 18px !important;
        box-shadow: 0 10px 30px rgba(59, 130, 246, 0.2) !important;
        backdrop-filter: blur(10px);
    }
    
    .stSuccess {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(52, 211, 153, 0.15) 100%) !important;
        border-left: 4px solid var(--success) !important;
        border-radius: 12px !important;
        padding: 18px !important;
        box-shadow: 0 10px 30px rgba(16, 185, 129, 0.2) !important;
        backdrop-filter: blur(10px);
    }
    
    .stWarning {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(251, 146, 60, 0.15) 100%) !important;
        border-left: 4px solid var(--warning) !important;
        border-radius: 12px !important;
        padding: 18px !important;
        box-shadow: 0 10px 30px rgba(245, 158, 11, 0.2) !important;
        backdrop-filter: blur(10px);
    }
    
    /* Columns spacing */
    [data-testid="column"] {
        padding: 12px;
    }
    
    /* Text styling */
    p {
        color: var(--text-secondary) !important;
        font-size: 1.05rem;
    }
    
    /* Subheader styling */
    .subtitle {
        color: var(--text-tertiary) !important;
        font-size: 1.1rem;
        margin-bottom: 25px;
        font-weight: 500;
        letter-spacing: 0.5px;
    }
    
    /* Metric value styling */
    [data-testid="metricValue"] {
        font-size: 2.5rem !important;
        font-weight: 900 !important;
        color: var(--text-primary) !important;
        background: linear-gradient(135deg, #f1f5f9 0%, #cbd5e1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    [data-testid="metricLabel"] {
        color: var(--text-tertiary) !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Divider styling */
    hr {
        border: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--dark-border), transparent);
        margin: 30px 0;
    }
    
    /* Professional card styling */
    .card {
        background: linear-gradient(135deg, #1a1a1a 0%, #000000 100%);
        padding: 24px;
        border-radius: 16px;
        border: 1px solid var(--dark-border);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.9), 0 0 60px rgba(99, 102, 241, 0.1);
        backdrop-filter: blur(10px);
    }
    
    .card:hover {
        box-shadow: 0 30px 60px rgba(0, 0, 0, 0.9), 0 0 100px rgba(99, 102, 241, 0.2);
        transform: translateY(-4px);
        border-color: var(--primary);
    }
    
    /* Tabs styling */
    button[kind="secondary"] {
        color: var(--text-secondary) !important;
        background-color: transparent !important;
        border: 1px solid var(--dark-border) !important;
    }
    
    button[kind="secondary"]:hover {
        background-color: rgba(99, 102, 241, 0.1) !important;
        border-color: var(--primary) !important;
    }
    </style>
""", unsafe_allow_html=True)

# ===== Header Section with Animation =====
st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
st.markdown("# 🎯 CHURN PREDICTION INTELLIGENCE")
st.markdown('<p class="subtitle">Advanced AI-Powered Customer Retention Analytics & Predictive Intelligence Platform</p>', unsafe_allow_html=True)


# ===== Sidebar Configuration =====
with st.sidebar:
    st.markdown("## ⚙️ DASHBOARD SETTINGS")
    st.markdown("---")
    
    theme_mode = st.radio("🎨 Theme", ["Dark", "Darker"], label_visibility="collapsed", horizontal=True)
    
    st.markdown("---")
    st.markdown("### 📊 Display Options")
    show_advanced = st.checkbox("🔬 Advanced Analytics", value=True)
    show_confidence = st.checkbox("📈 Confidence Scores", value=True)
    show_heatmap = st.checkbox("🔥 Risk Heatmap", value=False)
    
    st.markdown("---")
    st.markdown("### 🎯 Risk Thresholds")
    high_risk_threshold = st.slider("High Risk (%)", 0, 100, 70)
    low_risk_threshold = st.slider("Low Risk (%)", 0, 100, 30)
    
    st.markdown("---")
    st.markdown("### 📋 About")
    st.info("🚀 Enterprise-grade ML-powered customer churn prediction system with real-time analytics.")

# ===== File Upload Section =====
st.markdown("---")
st.markdown("## 📤 DATA INGESTION")

upload_col1, upload_col2, upload_col3 = st.columns([2, 1, 1])

with upload_col1:
    uploaded_file = st.file_uploader(
        "📁 Upload Customer CSV",
        type=["csv"],
        help="Select a CSV file containing customer behavioral and demographic data"
    )

with upload_col2:
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    if uploaded_file:
        st.success("✅ Ready")
    else:
        st.info("⏳ Waiting")

# ===== Main Analysis Section =====
if uploaded_file is not None:
    
    # Load and process data
    with st.spinner('🚀 Processing data with advanced ML models...'):
        progress_bar = st.progress(0)
        for i in range(100):
            progress_bar.progress(i + 1)
            time.sleep(0.005)
        
        df = pd.read_csv(uploaded_file)
        pipeline = PredictPipeline()
        predictions = pipeline.predict(df)
        kpi = ChurnKPI(predictions)
        results = kpi.compute_kpis()
        st.success("✅ Analysis complete!")
    
    # ===== Key Metrics Row =====
    st.markdown("---")
    st.markdown("## 📊 EXECUTIVE KPI SUMMARY")
    st.markdown('<p class="subtitle">Real-time business intelligence metrics</p>', unsafe_allow_html=True)
    
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5, gap="medium")
    
    with kpi_col1:
        st.metric(
            label="👥 Total Customers",
            value=f"{results['total_customers']:,}",
            delta="Active Base",
            delta_color="off"
        )
    
    with kpi_col2:
        high_risk_pct = (results["high_risk_customers"] / results['total_customers'] * 100) if results['total_customers'] > 0 else 0
        st.metric(
            label="🔴 HIGH RISK",
            value=results["high_risk_customers"],
            delta=f"{high_risk_pct:.1f}%",
            delta_color="inverse"
        )
    
    with kpi_col3:
        med_risk_pct = (results["medium_risk_customers"] / results['total_customers'] * 100) if results['total_customers'] > 0 else 0
        st.metric(
            label="🟡 MEDIUM RISK",
            value=results["medium_risk_customers"],
            delta=f"{med_risk_pct:.1f}%",
            delta_color="normal"
        )
    
    with kpi_col4:
        low_risk_pct = (results["low_risk_customers"] / results['total_customers'] * 100) if results['total_customers'] > 0 else 0
        st.metric(
            label="🟢 LOW RISK",
            value=results["low_risk_customers"],
            delta=f"{low_risk_pct:.1f}%",
            delta_color="off"
        )
    
    with kpi_col5:
        avg_churn = results["average_churn_probability"]
        st.metric(
            label="📊 AVG CHURN",
            value=f"{avg_churn:.1%}",
            delta="Probability",
            delta_color="off"
        )
    
    # ===== Advanced Analytics Section =====
    if show_advanced:
        st.markdown("---")
        st.markdown("## 🔬 ADVANCED ANALYTICS")
        st.markdown('<p class="subtitle">Deep-dive predictive intelligence and statistical analysis</p>', unsafe_allow_html=True)
        
        # Calculate additional metrics
        std_churn = predictions['churn_probability'].std()
        min_churn = predictions['churn_probability'].min()
        max_churn = predictions['churn_probability'].max()
        median_churn = predictions['churn_probability'].median()
        
        advanced_col1, advanced_col2, advanced_col3, advanced_col4 = st.columns(4, gap="medium")
        
        with advanced_col1:
            st.metric(
                label="📈 Std Deviation",
                value=f"{std_churn:.3f}",
                delta="Probability spread"
            )
        
        with advanced_col2:
            st.metric(
                label="📊 Median Risk",
                value=f"{median_churn:.1%}",
                delta="Central tendency"
            )
        
        with advanced_col3:
            st.metric(
                label="⚠️ Max Risk",
                value=f"{max_churn:.1%}",
                delta="Highest customer"
            )
        
        with advanced_col4:
            st.metric(
                label="✅ Min Risk",
                value=f"{min_churn:.1%}",
                delta="Lowest customer"
            )
    
    # ===== Visualization Dashboard =====
    st.markdown("---")
    st.markdown("## 📉 PREDICTIVE ANALYTICS VISUALIZATIONS")
    st.markdown('<p class="subtitle">Comprehensive risk distribution and trend analysis</p>', unsafe_allow_html=True)
    
    viz_col1, viz_col2 = st.columns(2, gap="large")
    
    with viz_col1:
        # Risk Distribution Pie Chart
        risk_data = {
            'Risk Level': ['🔴 High', '🟡 Medium', '🟢 Low'],
            'Count': [
                results['high_risk_customers'],
                results['medium_risk_customers'],
                results['low_risk_customers']
            ],
            'Color': ['#ef4444', '#f59e0b', '#10b981']
        }
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=risk_data['Risk Level'],
            values=risk_data['Count'],
            marker=dict(colors=risk_data['Color'], line=dict(color='#1e293b', width=2)),
            textposition='inside',
            textinfo='label+percent+value',
            textfont=dict(size=12, color='white', family='Arial Black'),
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )])
        
        fig_pie.update_layout(
            height=400,
            showlegend=True,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(size=13, color='#cbd5e1', family='Arial'),
            margin=dict(t=20, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': True})
    
    with viz_col2:
        # Churn Probability Distribution
        fig_hist = go.Figure(data=[go.Histogram(
            x=predictions['churn_probability'],
            nbinsx=40,
            marker=dict(
                color='#6366f1',
                opacity=0.85,
                line=dict(color='#4f46e5', width=1.5)
            ),
            textposition='auto',
            hovertemplate='Churn Range: %{x:.2%}<br>Count: %{y}<extra></extra>'
        )])
        
        # Add a reference line for average
        fig_hist.add_vline(
            x=results["average_churn_probability"],
            line_dash="dash",
            line_color="#ef4444",
            annotation_text=f"Avg: {results['average_churn_probability']:.1%}",
            annotation_position="top right"
        )
        
        fig_hist.update_layout(
            title='Churn Probability Distribution',
            xaxis_title='Churn Probability',
            yaxis_title='Customer Count',
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12, color='#cbd5e1', family='Arial'),
            showlegend=False,
            margin=dict(t=50, b=20, l=20, r=20)
        )
        fig_hist.update_xaxes(showgrid=False)
        fig_hist.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.05)')
        
        st.plotly_chart(fig_hist, use_container_width=True, config={'displayModeBar': True})
    
    # ===== Additional Visualizations =====
    viz_col3, viz_col4 = st.columns(2, gap="large")
    
    with viz_col3:
        # Box plot for risk distribution
        fig_box = go.Figure()
        
        for risk_level, color in [('High', '#ef4444'), ('Medium', '#f59e0b'), ('Low', '#10b981')]:
            risk_data = predictions[predictions['risk_level'] == risk_level]['churn_probability']
            fig_box.add_trace(go.Box(
                y=risk_data,
                name=f'🎯 {risk_level}',
                marker=dict(color=color, opacity=0.8),
                boxmean='sd',
                hovertemplate='%{y:.2%}<extra></extra>'
            ))
        
        fig_box.update_layout(
            title='Risk Segment Distribution Analysis',
            yaxis_title='Churn Probability',
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12, color='#cbd5e1'),
            showlegend=True,
            margin=dict(t=50, b=20, l=20, r=20)
        )
        fig_box.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.05)')
        
        st.plotly_chart(fig_box, use_container_width=True, config={'displayModeBar': True})
    
    with viz_col4:
        # Cumulative distribution
        sorted_probs = np.sort(predictions['churn_probability'].values)
        cumulative = np.arange(1, len(sorted_probs) + 1) / len(sorted_probs)
        
        fig_cumulative = go.Figure()
        fig_cumulative.add_trace(go.Scatter(
            x=sorted_probs,
            y=cumulative,
            mode='lines',
            name='Cumulative Distribution',
            line=dict(color='#6366f1', width=3),
            fill='tozeroy',
            fillcolor='rgba(99, 102, 241, 0.2)',
            hovertemplate='Risk: %{x:.2%}<br>Cumulative %: %{y:.1%}<extra></extra>'
        ))
        
        fig_cumulative.update_layout(
            title='Cumulative Risk Distribution',
            xaxis_title='Churn Probability',
            yaxis_title='Cumulative Percentage',
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12, color='#cbd5e1'),
            showlegend=False,
            margin=dict(t=50, b=20, l=20, r=20)
        )
        fig_cumulative.update_xaxes(showgrid=False)
        fig_cumulative.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.05)')
        
        st.plotly_chart(fig_cumulative, use_container_width=True, config={'displayModeBar': True})
    
    # ===== Data Preview =====
    st.markdown("---")
    st.markdown("## 📋 DATASET OVERVIEW")
    st.markdown('<p class="subtitle">Customer data snapshot and metadata</p>', unsafe_allow_html=True)
    
    preview_tab1, preview_tab2, preview_tab3 = st.tabs(["📊 Data Sample", "📈 Statistics", "🔍 Predictions"])
    
    with preview_tab1:
        st.dataframe(
            df.head(10),
            use_container_width=True,
            height=350
        )
    
    with preview_tab2:
        st.markdown("### Statistical Summary")
        st.dataframe(df.describe().T, use_container_width=True)
    
    with preview_tab3:
        pred_display = predictions.sort_values('churn_probability', ascending=False).head(15).copy()
        if 'churn_probability' in pred_display.columns:
            pred_display['Risk %'] = pred_display['churn_probability'].apply(lambda x: f"{x:.1%}")
        st.dataframe(pred_display, use_container_width=True, height=350)
    
    # ===== High Risk Alert Section =====
    st.markdown("---")
    st.markdown("## 🔴 CRITICAL ALERT: HIGH-RISK CUSTOMERS")
    st.markdown('<p class="subtitle">Immediate intervention recommended for retention</p>', unsafe_allow_html=True)
    
    high_risk_df = predictions[predictions["risk_level"] == "High"]
    
    if high_risk_df.empty:
        st.success("✅ EXCELLENT STATUS: No high-risk customers detected. Customer base is healthy and stable.")
    else:
        st.error(f"⚠️ ALERT: {len(high_risk_df)} high-risk customer(s) require immediate attention")
        
        # Risk severity breakdown
        alert_col1, alert_col2, alert_col3 = st.columns(3)
        
        with alert_col1:
            critical = len(high_risk_df[high_risk_df['churn_probability'] > 0.85])
            st.metric("🔴 CRITICAL (>85%)", critical)
        
        with alert_col2:
            severe = len(high_risk_df[(high_risk_df['churn_probability'] > 0.70) & (high_risk_df['churn_probability'] <= 0.85)])
            st.metric("🟠 SEVERE (70-85%)", severe)
        
        with alert_col3:
            high = len(high_risk_df[high_risk_df['churn_probability'] <= 0.70])
            st.metric("🟡 HIGH (<70%)", high)
        
        st.markdown("### Top 25 Most At-Risk Customers")
        display_high_risk = high_risk_df.sort_values(by="churn_probability", ascending=False).head(25).copy()
        
        if 'churn_probability' in display_high_risk.columns:
            display_high_risk['Risk Score %'] = display_high_risk['churn_probability'].apply(lambda x: f"{x:.1%}")
            display_high_risk = display_high_risk.drop('churn_probability', axis=1)
        
        st.dataframe(
            display_high_risk,
            use_container_width=True,
            height=450,
            hide_index=True
        )
    
    # ===== Export & Download Center =====
    st.markdown("---")
    st.markdown("## 💾 DATA EXPORT CENTER")
    st.markdown('<p class="subtitle">Download predictions and analytics reports</p>', unsafe_allow_html=True)
    
    export_col1, export_col2, export_col3, export_col4 = st.columns(4, gap="medium")
    
    with export_col1:
        csv = predictions.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 All Predictions",
            data=csv,
            file_name=f"churn_predictions_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with export_col2:
        if not high_risk_df.empty:
            high_risk_csv = high_risk_df.sort_values(by="churn_probability", ascending=False).to_csv(index=False).encode("utf-8")
            st.download_button(
                label="🔴 High-Risk Only",
                data=high_risk_csv,
                file_name=f"high_risk_customers_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.button("🔴 High-Risk Only", disabled=True)
    
    with export_col3:
        summary_text = f"""
╔════════════════════════════════════════════════════════════╗
║    CUSTOMER CHURN ANALYSIS REPORT - EXECUTIVE SUMMARY      ║
╚════════════════════════════════════════════════════════════╝

📊 ANALYSIS METADATA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Analysis Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
Platform: Enterprise Churn Prediction System v2.0
Model: Advanced ML Ensemble Classifier

👥 CUSTOMER BASE METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Customers: {results['total_customers']:,}
Analysis Coverage: 100% of database

🎯 RISK SEGMENTATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 HIGH RISK:     {results['high_risk_customers']:>6} customers ({results['high_risk_customers']/results['total_customers']*100:>5.1f}%)
🟡 MEDIUM RISK:   {results['medium_risk_customers']:>6} customers ({results['medium_risk_customers']/results['total_customers']*100:>5.1f}%)
🟢 LOW RISK:      {results['low_risk_customers']:>6} customers ({results['low_risk_customers']/results['total_customers']*100:>5.1f}%)

📈 CHURN PROBABILITY ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Average Churn Probability:  {results['average_churn_probability']:.1%}
Median Churn Probability:   {median_churn:.1%}
Maximum Risk Level:         {max_churn:.1%}
Minimum Risk Level:         {min_churn:.1%}
Standard Deviation:         {std_churn:.3f}

💡 RECOMMENDED ACTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Immediate intervention for {results['high_risk_customers']} high-risk customers
2. Implement targeted retention programs
3. Schedule customer success reviews
4. Develop personalized engagement strategies
5. Monitor medium-risk segment for escalation

════════════════════════════════════════════════════════════
Generated by: Churn Prediction Intelligence System
════════════════════════════════════════════════════════════
        """
        st.download_button(
            label="📄 Executive Summary",
            data=summary_text.encode("utf-8"),
            file_name=f"churn_summary_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
    
    with export_col4:
        json_data = predictions.to_json(orient='records').encode("utf-8")
        st.download_button(
            label="📋 JSON Format",
            data=json_data,
            file_name=f"churn_predictions_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    # ===== Footer =====
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 30px 20px;'>
        <div style='color: #94a3b8; font-size: 0.95rem; line-height: 1.8;'>
            <p style='margin: 8px 0;'><strong>🚀 ENTERPRISE CHURN PREDICTION PLATFORM</strong></p>
            <p style='margin: 8px 0; color: #64748b; font-size: 0.9rem;'>Powered by Advanced Machine Learning | Real-Time Analytics | Predictive Intelligence</p>
            <p style='margin: 8px 0; color: #475569; font-size: 0.85rem;'>Analysis completed with enterprise-grade accuracy and security standards</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    # ===== Professional Empty State =====
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 80px 40px; background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%); border-radius: 20px; border: 2px dashed rgba(99, 102, 241, 0.3);'>
            <div style='font-size: 4rem; margin-bottom: 25px;'>🚀</div>
            <h2 style='color: #f1f5f9; margin-bottom: 15px; font-size: 2rem;'>WELCOME TO CHURN INTELLIGENCE</h2>
            <p style='color: #cbd5e1; margin-bottom: 35px; font-size: 1.15rem; line-height: 1.6;'>
                Enterprise-grade AI-powered predictive analytics platform for customer churn forecasting
            </p>
            <div style='background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 30px; border-radius: 12px; border: 1px solid #334155; text-align: left; display: inline-block; margin-bottom: 30px;'>
                <h4 style='color: #f1f5f9; margin-bottom: 15px;'>🎯 KEY PLATFORM FEATURES</h4>
                <ul style='list-style: none; padding: 0; margin: 0;'>
                    <li style='color: #cbd5e1; margin: 10px 0; padding-left: 30px; position: relative;'>
                        <span style='position: absolute; left: 0;'>✅</span>
                        <strong>Advanced ML Models</strong> - State-of-the-art ensemble classifiers
                    </li>
                    <li style='color: #cbd5e1; margin: 10px 0; padding-left: 30px; position: relative;'>
                        <span style='position: absolute; left: 0;'>✅</span>
                        <strong>Real-Time Analytics</strong> - Instant customer risk assessment
                    </li>
                    <li style='color: #cbd5e1; margin: 10px 0; padding-left: 30px; position: relative;'>
                        <span style='position: absolute; left: 0;'>✅</span>
                        <strong>Risk Segmentation</strong> - High, medium, low-risk categorization
                    </li>
                    <li style='color: #cbd5e1; margin: 10px 0; padding-left: 30px; position: relative;'>
                        <span style='position: absolute; left: 0;'>✅</span>
                        <strong>Export Capabilities</strong> - CSV, JSON, summary reports
                    </li>
                    <li style='color: #cbd5e1; margin: 10px 0; padding-left: 30px; position: relative;'>
                        <span style='position: absolute; left: 0;'>✅</span>
                        <strong>Interactive Visualizations</strong> - Comprehensive data analysis
                    </li>
                    <li style='color: #cbd5e1; margin: 10px 0; padding-left: 30px; position: relative;'>
                        <span style='position: absolute; left: 0;'>✅</span>
                        <strong>Predictive Intelligence</strong> - Actionable retention insights
                    </li>
                </ul>
            </div>
            <p style='color: #94a3b8; font-size: 1rem;'> 👆 Upload a CSV file to begin your analysis</p>
        </div>
        """, unsafe_allow_html=True)
