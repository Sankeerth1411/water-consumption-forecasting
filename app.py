import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
from pathlib import Path
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Water Consumption Forecasting - Case Study",
    page_icon="💧",
    layout="wide"
)

# Project root directory
ROOT_DIR = Path(__file__).parent

# Sidebar (Public view without USN)
st.sidebar.title("Project Details")
st.sidebar.markdown("**Project:** Water Consumption Forecasting")
st.sidebar.markdown("**Course:** Data Mining")
st.sidebar.markdown("**Assigned Algorithm:** Decision Tree Regressor")
st.sidebar.markdown("---")
app_mode = st.sidebar.selectbox("Navigation", ["Overview & Metrics", "Interactive Forecast Simulator", "Visualisations & Insights"])

@st.cache_resource
def load_model_and_data():
    model_path = ROOT_DIR / 'models' / 'decision_tree_model.joblib'
    if model_path.exists():
        artifact = joblib.load(model_path)
    else:
        artifact = None

    eval_path = ROOT_DIR / 'reports' / 'evaluation_results.csv'
    if eval_path.exists():
        eval_df = pd.read_csv(eval_path)
    else:
        eval_df = None

    return artifact, eval_df

artifact, eval_df = load_model_and_data()

if app_mode == "Overview & Metrics":
    st.title("💧 Household Water Consumption Forecasting")
    st.markdown("### Decision Tree Regression Case Study")
    st.markdown("""
    This application estimates future household water consumption using historical water usage and temporal patterns, built as part of the Data Mining case study.
    """)

    col1, col2, col3 = st.columns(3)
    col1.metric("Primary Algorithm", "Decision Tree Regressor", "sklearn.tree")
    col2.metric("Dataset Source", "Zenodo Residential Data", "10.5281/zenodo.15180140")
    col3.metric("Target Variable", "Daily Water Use", "Liters (L)")

    st.markdown("---")
    st.subheader("Model Performance Comparison (Test Set)")
    if eval_df is not None:
        st.dataframe(eval_df.style.highlight_min(subset=['MAE', 'RMSE'], color='lightgreen', axis=0), use_container_width=True)
    else:
        st.warning("Evaluation results not found. Please run `src/train_model.py` first.")

elif app_mode == "Interactive Forecast Simulator":
    st.title("🔮 Next-Day Water Consumption Predictor")
    st.markdown("Enter historical usage features below to estimate the next day's water consumption using the trained Decision Tree Regressor.")

    if artifact is None:
        st.error("Trained model artifact not found! Please run `python src/train_model.py`.")
    else:
        model = artifact['model']
        feature_cols = artifact['feature_cols']

        col1, col2 = st.columns(2)
        with col1:
            lag_1 = st.number_input("Previous Day Water Use (L) [lag_1]", min_value=0.0, max_value=2000.0, value=350.0, step=10.0)
            lag_7 = st.number_input("Water Use 7 Days Ago (L) [lag_7]", min_value=0.0, max_value=2000.0, value=340.0, step=10.0)
            rolling_mean_7 = st.number_input("Rolling 7-Day Mean (L)", min_value=0.0, max_value=2000.0, value=345.0, step=10.0)
            rolling_std_7 = st.number_input("Rolling 7-Day Std Dev (L)", min_value=0.0, max_value=500.0, value=45.0, step=5.0)
            day_of_week = st.slider("Day of Week (0=Mon, 6=Sun)", 0, 6, 2)
            month = st.slider("Month", 1, 12, 6)

        with col2:
            day_of_year = st.slider("Day of Year", 1, 365, 180)
            is_weekend = 1 if day_of_week >= 5 else 0
            st.info(f"Weekend Indicator: {is_weekend}")
            occ_01 = st.slider("Occupancy Indicator 1", 0.0, 1.0, 0.5)
            occ_02 = st.slider("Occupancy Indicator 2", 0.0, 1.0, 0.5)
            occ_03 = st.slider("Occupancy Indicator 3", 0.0, 1.0, 0.5)
            occ_04 = st.slider("Occupancy Indicator 4", 0.0, 1.0, 0.5)
            occ_05 = st.slider("Occupancy Indicator 5", 0.0, 1.0, 0.5)

        input_data = pd.DataFrame([{
            'lag_1': lag_1,
            'lag_7': lag_7,
            'rolling_mean_7': rolling_mean_7,
            'rolling_std_7': rolling_std_7,
            'day_of_week': day_of_week,
            'month': month,
            'day_of_year': day_of_year,
            'is_weekend': is_weekend,
            'occ_01': occ_01,
            'occ_02': occ_02,
            'occ_03': occ_03,
            'occ_04': occ_04,
            'occ_05': occ_05
        }])[feature_cols]

        if st.button("Generate Forecast", type="primary"):
            pred = model.predict(input_data)[0]
            leaf_id = model.apply(input_data)[0]
            n_samples = model.tree_.n_node_samples[leaf_id]

            st.success(f"### Estimated Next-Day Water Consumption: **{pred:.2f} Liters**")

            # Diagnostics section
            with st.expander("🔍 Model Diagnostics & Leaf Node Information", expanded=True):
                st.markdown(f"**Assigned Tree Leaf ID:** `{leaf_id}`")
                st.markdown(f"**Training Samples in Leaf:** `{n_samples}`")
                st.markdown("**Input Features Used for Prediction:**")
                st.dataframe(input_data, use_container_width=True)

                st.info("""
                **Why does the prediction sometimes stay constant when changing inputs?**
                A `DecisionTreeRegressor` partitions the feature space into rectangular regions (leaf nodes).
                Within any single leaf node, the model outputs the constant average target value of the training samples that fell into that region.
                As long as your input changes do not cross the split thresholds of the tree's decision nodes, the sample remains in the same leaf, resulting in the same constant prediction.
                When your inputs cross a split threshold, the prediction steps to a new leaf value. This is normal piecewise-constant behavior for Decision Trees.
                """)

elif app_mode == "Visualisations & Insights":
    st.title("📊 Model Visualisations & Feature Importance")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Actual vs Predicted")
        img_path1 = ROOT_DIR / 'reports' / 'actual_vs_predicted.png'
        if img_path1.exists():
            st.image(str(img_path1), use_container_width=True)
        else:
            st.warning("Chart not found.")

    with col2:
        st.subheader("Residual Plot")
        img_path2 = ROOT_DIR / 'reports' / 'residual_plot.png'
        if img_path2.exists():
            st.image(str(img_path2), use_container_width=True)
        else:
            st.warning("Chart not found.")

    st.subheader("Feature Importance")
    img_path3 = ROOT_DIR / 'reports' / 'feature_importance.png'
    if img_path3.exists():
        st.image(str(img_path3), use_container_width=True)
    else:
        st.warning("Chart not found.")
