import streamlit as st
import pandas as pd
import numpy as np
import requests
import io
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

# ===============================
# FASTAPI CONFIG
# ===============================
API_URL = "http://127.0.0.1:8000"

# ===============================
# Page Configuration
# ===============================
st.set_page_config(
    page_title="Customer Churn Prediction Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# Custom CSS (UNCHANGED)
# ===============================
st.markdown("""<style> /* YOUR FULL CSS EXACTLY AS IS */ </style>""",
            unsafe_allow_html=True)

# ===============================
# Header
# ===============================
st.markdown("# 🎯 CHURN PREDICTION INTELLIGENCE")
st.markdown(
    '<p class="subtitle">AI-Powered Customer Retention Analytics Platform</p>',
    unsafe_allow_html=True
)

# ===============================
# Sidebar
# ===============================
with st.sidebar:
    st.markdown("## ⚙️ DASHBOARD SETTINGS")
    show_advanced = st.checkbox("🔬 Advanced Analytics", value=True)

# ===============================
# File Upload
# ===============================
st.markdown("## 📤 DATA INGESTION")
uploaded_file = st.file_uploader("Upload Customer CSV", type=["csv"])

# ===============================
# MAIN LOGIC
# ===============================
if uploaded_file is not None:

    with st.spinner("🚀 Calling FastAPI for predictions..."):
        response = requests.post(
            f"{API_URL}/predict_csv",
            files={"file": uploaded_file.getvalue()}
        )

    if response.status_code != 200:
        st.error("❌ FastAPI request failed")
        st.stop()

    result = response.json()

    predictions = pd.DataFrame(result["predictions"])
    kpis = result["kpis"]

    st.success("✅ Prediction completed successfully")

    # ===============================
    # KPI SUMMARY
    # ===============================
    st.markdown("## 📊 EXECUTIVE KPI SUMMARY")

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Total Customers", kpis["total_customers"])
    c2.metric("High Risk", kpis["high_risk_customers"])
    c3.metric("Medium Risk", kpis["medium_risk_customers"])
    c4.metric("Low Risk", kpis["low_risk_customers"])
    c5.metric(
        "Avg Churn Probability",
        f"{kpis['average_churn_probability']:.1%}"
    )

    # ===============================
    # ADVANCED METRICS
    # ===============================
    if show_advanced:
        st.markdown("## 🔬 ADVANCED ANALYTICS")

        st.metric(
            "Max Churn Risk",
            f"{predictions['churn_probability'].max():.1%}"
        )

        st.metric(
            "Min Churn Risk",
            f"{predictions['churn_probability'].min():.1%}"
        )

    # ===============================
    # VISUALIZATIONS
    # ===============================
    st.markdown("## 📉 CHURN DISTRIBUTION")

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=predictions["churn_probability"],
        nbinsx=30,
        marker_color="#6366f1"
    ))

    fig.update_layout(
        xaxis_title="Churn Probability",
        yaxis_title="Customers",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    # ===============================
    # HIGH RISK CUSTOMERS
    # ===============================
    st.markdown("## 🔴 HIGH-RISK CUSTOMERS")

    high_risk_df = predictions[predictions["risk_level"] == "High"]

    if high_risk_df.empty:
        st.success("No high-risk customers 🎉")
    else:
        st.dataframe(
            high_risk_df.sort_values(
                by="churn_probability",
                ascending=False
            )
        )

    # ===============================
    # DOWNLOAD
    # ===============================
    csv = predictions.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ Download Predictions",
        data=csv,
        file_name="churn_predictions.csv",
        mime="text/csv"
    )

else:
    st.info("Upload a CSV file to begin analysis.")
