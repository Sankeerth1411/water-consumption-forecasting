Update README.md with the actual live Streamlit URL:

https://water-consumption-forecasting-kqpyd7odm2tszptaoaw7t8.streamlit.app/

Add a prominent Live Demo section near the top.
Commit and push the README update to main.
Do not modify the working application.
# Household Water Consumption Forecasting Using Decision Tree Regression

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.66-red.svg)](https://streamlit.io)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.9-orange.svg)](https://scikit-learn.org/)
[![License: CC-BY](https://img.shields.io/badge/License-CC%20BY-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

## Overview
This repository contains an end-to-end data mining case study focused on forecasting daily residential water consumption using historical usage patterns and environmental/temporal features. Built as part of the Data Mining course practical work, the project features a rigorously trained Decision Tree Regressor (`sklearn.tree.DecisionTreeRegressor`), comprehensive data preprocessing, leakage-free feature engineering, and an interactive Streamlit web application.

---

## Problem Statement
Given historical daily water consumption time-series data and occupancy indicator features across residential households, build a robust supervised machine learning regression model to predict the next calendar day's total water consumption (in liters) for a given household, utilizing only information available prior to the prediction date without data leakage.

---

## Objectives
1. Acquire, inspect, and audit the public Zenodo residential water consumption and occupancy dataset (Record 15180141).
2. Execute a reproducible data preprocessing and daily aggregation pipeline.
3. Perform leak-free chronological feature engineering, constructing lagged consumption variables and rolling window statistics.
4. Train, hyperparameter-tune, and evaluate a Decision Tree Regressor adhering strictly to chronological train, validation, and test splits.
5. Benchmark against persistence baselines and linear regression.
6. Deploy an interactive Streamlit web application for real-time forecasting and model introspection.

---

## Dataset Source & Citation
- **Dataset:** Residential Household Dataset: Occupancy, Water, and Electricity Data
- **Repository:** Zenodo
- **Record ID:** [15180141](https://zenodo.org/records/15180141)
- **DOI:** [10.5281/zenodo.15180140](https://doi.org/10.5281/zenodo.15180140)

---

## Methodology & Feature Engineering
- **Daily Aggregation:** High-resolution hourly metered readings were aggregated into daily consumption totals (Liters) per building.
- **Leak-Free Lags:** Constructed `lag_1` (previous day consumption) and `lag_7` (consumption 7 days prior) via shifted building groups.
- **Rolling Statistics:** Computed 7-day rolling mean (`rolling_mean_7`) and standard deviation (`rolling_std_7`) on past shifted data.
- **Temporal Features:** Extracted day of week, month, day of year, and weekend indicators.
- **Chronological Split:** 70% Training (Jan–Sep), 15% Validation (Sep–Nov), 15% Testing (Nov–Dec).

---

## Model Evaluation & Performance Comparison
Evaluated on an untouched chronological test set (540 samples):

| Model | MAE (L) | RMSE (L) | R² Score |
|---|---|---|---|
| Baseline (Lag-1) | 104.46 | 143.33 | -0.0144 |
| Baseline (Lag-7) | 114.90 | 161.66 | -0.2903 |
| Linear Regression | **87.58** | **119.42** | **0.2958** |
| **Decision Tree Regressor (Assigned)** | **88.60** | **121.71** | **0.2686** |

*Note: While Linear Regression achieves a slightly higher R², the Decision Tree Regressor provides superior explainability via hierarchical decision rules and feature importance rankings while substantially outperforming persistence baselines.*

---

## Project Structure
```text
water-consumption-forecasting/
├── models/
│   └── decision_tree_model.joblib
├── reports/
│   ├── evaluation_results.csv
│   ├── actual_vs_predicted.png
│   ├── residual_plot.png
│   └── feature_importance.png
├── src/
│   ├── data_processing.py
│   ├── train_model.py
│   └── evaluate_model.py
├── app.py
├── requirements.txt
└── README.md
```

---

## Installation & Local Execution
1. Clone the repository:
   ```bash
   git clone https://github.com/Sankeerth1411/water-consumption-forecasting.git
   cd water-consumption-forecasting
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Streamlit application locally:
   ```bash
   streamlit run app.py
   ```

---

## Cloud Deployment (Streamlit Community Cloud)
1. Push repository to GitHub.
2. Visit [Share Streamlit](https://share.streamlit.io).
3. Connect repository, select branch `main`, and set main file path to `app.py`.
4. Deploy!

- **Live Application URL:** [Streamlit Community Cloud Dashboard](https://share.streamlit.io) *(Configure and launch via Streamlit Cloud)*

---

## Limitations & Future Enhancements
- **Limitations:** Anonymized residential data lacks exact geographic coordinates for external weather API integration; decision trees exhibit piecewise-constant quantization.
- **Future Enhancements:** Integration of IoT smart-meter streaming APIs and gradient-boosted ensemble architectures.
