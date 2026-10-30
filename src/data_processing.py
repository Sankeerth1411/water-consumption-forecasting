import pandas as pd
import numpy as np
import os

def process_data(raw_path='data/raw/final_data/daily_data.csv', output_dir='data/processed'):
    os.makedirs(output_dir, exist_ok=True)

    print(f"Loading raw data from {raw_path}...")
    df = pd.read_csv(raw_path)

    # Ensure datetime format and numeric occupancy
    df['date'] = pd.to_datetime(df['date'])
    occupancy_cols = [c for c in df.columns if c.startswith('occ_')]
    for col in occupancy_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    agg_dict = {'water_use_l': 'sum'}
    for col in occupancy_cols:
        agg_dict[col] = 'mean'

    daily_df = df.groupby(['building', 'date']).agg(agg_dict).reset_index()
    daily_df = daily_df.sort_values(['building', 'date']).reset_index(drop=True)

    print(f"Daily aggregated shape: {daily_df.shape}")

    # Feature Engineering per building
    print("Engineering lag features and rolling statistics...")
    features_list = []

    for building, group in daily_df.groupby('building'):
        group = group.copy()

        # Target variable: today's water consumption
        group['target'] = group['water_use_l']

        # Lag features (shifted by 1 day to prevent leakage)
        group['lag_1'] = group['water_use_l'].shift(1)
        group['lag_7'] = group['water_use_l'].shift(7)

        # Rolling statistics (past 7 days, shifted by 1)
        shifted_water = group['water_use_l'].shift(1)
        group['rolling_mean_7'] = shifted_water.rolling(window=7, min_periods=1).mean()
        group['rolling_std_7'] = shifted_water.rolling(window=7, min_periods=1).std().fillna(0)

        # Calendar features
        group['day_of_week'] = group['date'].dt.day_of_week
        group['month'] = group['date'].dt.month
        group['day_of_year'] = group['date'].dt.day_of_year
        group['is_weekend'] = group['day_of_week'].isin([5, 6]).astype(int)

        features_list.append(group)

    processed_df = pd.concat(features_list, ignore_index=True)

    # Drop rows with NaN in lags (first 7 days of each building)
    processed_df = processed_df.dropna(subset=['lag_1', 'lag_7', 'rolling_mean_7']).reset_index(drop=True)

    print(f"Processed dataset shape after lag creation: {processed_df.shape}")

    # Save full processed dataset
    processed_df.to_csv(os.path.join(output_dir, 'processed_daily_data.csv'), index=False)

    # Chronological Split (70% Train, 15% Validation, 15% Test based on dates)
    dates = np.sort(processed_df['date'].unique())
    n_dates = len(dates)

    train_end_idx = int(n_dates * 0.70)
    val_end_idx = int(n_dates * 0.85)

    train_dates = dates[:train_end_idx]
    val_dates = dates[train_end_idx:val_end_idx]
    test_dates = dates[val_end_idx:]

    train_df = processed_df[processed_df['date'].isin(train_dates)]
    val_df = processed_df[processed_df['date'].isin(val_dates)]
    test_df = processed_df[processed_df['date'].isin(test_dates)]

    print(f"Train split: {train_df.shape[0]} rows (Dates: {pd.to_datetime(train_dates[0]).date()} to {pd.to_datetime(train_dates[-1]).date()})")
    print(f"Val split:   {val_df.shape[0]} rows (Dates: {pd.to_datetime(val_dates[0]).date()} to {pd.to_datetime(val_dates[-1]).date()})")
    print(f"Test split:  {test_df.shape[0]} rows (Dates: {pd.to_datetime(test_dates[0]).date()} to {pd.to_datetime(test_dates[-1]).date()})")

    train_df.to_csv(os.path.join(output_dir, 'train.csv'), index=False)
    val_df.to_csv(os.path.join(output_dir, 'val.csv'), index=False)
    test_df.to_csv(os.path.join(output_dir, 'test.csv'), index=False)

    print("Data processing and chronological split completed successfully.")

if __name__ == '__main__':
    process_data()
