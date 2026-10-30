import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os

def generate_visualisations():
    os.makedirs('reports', exist_ok=True)

    # Load model and test set
    model_artifact = joblib.load('models/decision_tree_model.joblib')
    model = model_artifact['model']
    feature_cols = model_artifact['feature_cols']

    test_df = pd.read_csv('data/processed/test.csv')
    X_test = test_df[feature_cols]
    y_test = test_df['target']

    predictions = model.predict(X_test)
    residuals = y_test - predictions

    # Set style
    sns.set_theme(style='whitegrid')

    # 1. Actual vs Predicted Plot
    plt.figure(figsize=(8, 6))
    plt.scatter(y_test, predictions, alpha=0.5, color='teal', edgecolor='k')
    min_val = min(y_test.min(), predictions.min())
    max_val = max(y_test.max(), predictions.max())
    plt.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Ideal Fit')
    plt.xlabel('Actual Water Consumption (L)', fontsize=12)
    plt.ylabel('Predicted Water Consumption (L)', fontsize=12)
    plt.title('Actual vs. Predicted Daily Water Consumption (Decision Tree)', fontsize=14, fontweight='bold')
    plt.legend()
    plt.tight_layout()
    plt.savefig('reports/actual_vs_predicted.png', dpi=300)
    plt.close()

    # 2. Residual Plot
    plt.figure(figsize=(8, 6))
    plt.scatter(predictions, residuals, alpha=0.5, color='purple', edgecolor='k')
    plt.axhline(0, color='r', linestyle='--', lw=2)
    plt.xlabel('Predicted Water Consumption (L)', fontsize=12)
    plt.ylabel('Residuals (Actual - Predicted)', fontsize=12)
    plt.title('Residual Plot (Decision Tree Regressor)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('reports/residual_plot.png', dpi=300)
    plt.close()

    # 3. Feature Importance Chart
    importances = model.feature_importances_
    feat_imp = pd.DataFrame({'Feature': feature_cols, 'Importance': importances})
    feat_imp = feat_imp.sort_values(by='Importance', ascending=False)

    plt.figure(figsize=(10, 6))
    sns.barplot(x='Importance', y='Feature', data=feat_imp, palette='viridis')
    plt.title('Decision Tree Feature Importance', fontsize=14, fontweight='bold')
    plt.xlabel('Importance Score', fontsize=12)
    plt.ylabel('Feature', fontsize=12)
    plt.tight_layout()
    plt.savefig('reports/feature_importance.png', dpi=300)
    plt.close()

    print("Generated visualisations successfully in reports/")

if __name__ == '__main__':
    generate_visualisations()
