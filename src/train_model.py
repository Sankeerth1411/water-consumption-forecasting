import pandas as pd
import numpy as np
import os
import joblib
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def train_and_evaluate():
    data_dir = 'data/processed'
    models_dir = 'models'
    os.makedirs(models_dir, exist_ok=True)

    print("Loading training, validation, and test sets...")
    train_df = pd.read_csv(os.path.join(data_dir, 'train.csv'))
    val_df = pd.read_csv(os.path.join(data_dir, 'val.csv'))
    test_df = pd.read_csv(os.path.join(data_dir, 'test.csv'))

    # Define features and target
    feature_cols = [
        'lag_1', 'lag_7', 'rolling_mean_7', 'rolling_std_7',
        'day_of_week', 'month', 'day_of_year', 'is_weekend',
        'occ_01', 'occ_02', 'occ_03', 'occ_04', 'occ_05'
    ]
    target_col = 'target'

    X_train, y_train = train_df[feature_cols], train_df[target_col]
    X_val, y_val = val_df[feature_cols], val_df[target_col]
    X_test, y_test = test_df[feature_cols], test_df[target_col]

    # Hyperparameter tuning on validation set
    print("Tuning Decision Tree Regressor hyperparameters on validation set...")
    best_mae = float('inf')
    best_params = {}
    best_model = None

    depths = [3, 5, 8, 12]
    min_samples_splits = [5, 10]
    min_samples_leaves = [5, 10]

    for depth in depths:
        for mss in min_samples_splits:
            for msl in min_samples_leaves:
                dt = DecisionTreeRegressor(
                    max_depth=depth,
                    min_samples_split=mss,
                    min_samples_leaf=msl,
                    random_state=42
                )
                dt.fit(X_train, y_train)
                val_preds = dt.predict(X_val)
                val_mae = mean_absolute_error(y_val, val_preds)

                if val_mae < best_mae:
                    best_mae = val_mae
                    best_params = {'max_depth': depth, 'min_samples_split': mss, 'min_samples_leaf': msl}
                    best_model = dt

    print(f"Best Validation MAE: {best_mae:.4f}")
    print(f"Best Hyperparameters: {best_params}")

    # Retrain best model on Train + Validation (or keep train-trained best model; let's train on train+val for final model)
    X_train_val = pd.concat([X_train, X_val], ignore_index=True)
    y_train_val = pd.concat([y_train, y_val], ignore_index=True)

    final_tree = DecisionTreeRegressor(
        max_depth=best_params['max_depth'],
        min_samples_split=best_params['min_samples_split'],
        min_samples_leaf=best_params['min_samples_leaf'],
        random_state=42
    )
    final_tree.fit(X_train_val, y_train_val)

    # Save model and feature schema
    model_artifact = {
        'model': final_tree,
        'feature_cols': feature_cols,
        'best_params': best_params
    }
    model_path = os.path.join(models_dir, 'decision_tree_model.joblib')
    joblib.dump(model_artifact, model_path)
    print(f"Saved trained Decision Tree model to {model_path}")

    # Evaluate on Test Set
    print("\n--- TEST SET EVALUATION ---")
    test_preds = final_tree.predict(X_test)
    test_mae = mean_absolute_error(y_test, test_preds)
    test_rmse = np.sqrt(mean_squared_error(y_test, test_preds))
    test_r2 = r2_score(y_test, test_preds)

    print(f"Decision Tree Test MAE:  {test_mae:.4f} L")
    print(f"Decision Tree Test RMSE: {test_rmse:.4f} L")
    print(f"Decision Tree Test R²:   {test_r2:.4f}")

    # Baseline 1: Previous-day consumption (lag_1)
    b1_preds = test_df['lag_1'].values
    b1_mae = mean_absolute_error(y_test, b1_preds)
    b1_rmse = np.sqrt(mean_squared_error(y_test, b1_preds))
    b1_r2 = r2_score(y_test, b1_preds)
    print(f"Baseline (Lag-1) MAE:  {b1_mae:.4f} L | RMSE: {b1_rmse:.4f} L | R²: {b1_r2:.4f}")

    # Baseline 2: Consumption 7 days earlier (lag_7)
    b2_preds = test_df['lag_7'].values
    b2_mae = mean_absolute_error(y_test, b2_preds)
    b2_rmse = np.sqrt(mean_squared_error(y_test, b2_preds))
    b2_r2 = r2_score(y_test, b2_preds)
    print(f"Baseline (Lag-7) MAE:  {b2_mae:.4f} L | RMSE: {b2_rmse:.4f} L | R²: {b2_r2:.4f}")

    # Baseline 3: Linear Regression
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    lr_preds = lr.predict(X_test)
    lr_mae = mean_absolute_error(y_test, lr_preds)
    lr_rmse = np.sqrt(mean_squared_error(y_test, lr_preds))
    lr_r2 = r2_score(y_test, lr_preds)
    print(f"Linear Regression MAE: {lr_mae:.4f} L | RMSE: {lr_rmse:.4f} L | R²: {lr_r2:.4f}")

    # Save evaluation summary table
    eval_summary = pd.DataFrame([
        {'Model': 'Baseline (Lag-1)', 'MAE': b1_mae, 'RMSE': b1_rmse, 'R2': b1_r2},
        {'Model': 'Baseline (Lag-7)', 'MAE': b2_mae, 'RMSE': b2_rmse, 'R2': b2_r2},
        {'Model': 'Linear Regression', 'MAE': lr_mae, 'RMSE': lr_rmse, 'R2': lr_r2},
        {'Model': 'Decision Tree Regressor (Assigned)', 'MAE': test_mae, 'RMSE': test_rmse, 'R2': test_r2},
    ])
    os.makedirs('reports', exist_ok=True)
    eval_summary.to_csv('reports/evaluation_results.csv', index=False)
    print("Saved evaluation summary to reports/evaluation_results.csv")

if __name__ == '__main__':
    train_and_evaluate()
