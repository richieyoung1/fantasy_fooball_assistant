import pandas as pd
import os
from sklearn.ensemble import RandomForestRegressor
import numpy as np

# 🎯 Target stat columns
TARGET_COLUMNS = ["pass_yards", "pass_tds", "rush_yards", "rush_tds", "fantasy_points"]

def load_and_merge(year, include_stats=True):
    if include_stats:
        stats = pd.read_csv(f"qb_{year}_stats.csv")
    else:
        stats = pd.DataFrame()

    features = pd.read_csv(f"qb_{year}_features.csv")
    advanced = pd.read_csv(f"qb_advanced_{year}.csv")

    for df in [stats, features, advanced]:
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

    # Merge dataframes
    if include_stats:
        df = stats.merge(features, on="player").merge(advanced, on="player")
        df["pass_yards"] = pd.to_numeric(df["pass_yards"], errors="coerce").fillna(0)
        df["pass_tds"] = pd.to_numeric(df["pass_tds"], errors="coerce").fillna(0)
        df["interceptions"] = pd.to_numeric(df["interceptions"], errors="coerce").fillna(0)
        df["rush_yards"] = pd.to_numeric(df["rush_yards"], errors="coerce").fillna(0)
        df["rush_tds"] = pd.to_numeric(df["rush_tds"], errors="coerce").fillna(0)

        df["fantasy_points"] = (
            0.04 * df["pass_yards"] +
            4 * df["pass_tds"] +
            -1 * df["interceptions"] +
            0.1 * df["rush_yards"] +
            6 * df["rush_tds"]
        )
    else:
        df = features.merge(advanced, on="player")

    return df

def prepare_data(df, target_columns=None):
    df.columns = [col.lower().strip().replace(" ", "_") for col in df.columns]

    X = df.select_dtypes(include=[np.number])
    y = df[target_columns] if target_columns else None
    return X, y

def main():
    print("\n🧠 Training on 2020–2024 data...")

    all_train = []
    for year in range(2020, 2025):
        df = load_and_merge(year)
        all_train.append(df)
        print(f"✅ Loaded {year} data: {df.shape}")
    
    train_df = pd.concat(all_train, ignore_index=True)
    X_train, _ = prepare_data(train_df, TARGET_COLUMNS)
    y_train = train_df[TARGET_COLUMNS]

    print("\n🔁 Using 2024 player features for 2025 prediction...")
    test_df = load_and_merge(2024, include_stats=False)
    players = test_df["player"]
    X_test, _ = prepare_data(test_df)

    # Match feature columns (if mismatch in column order/names)
    common_cols = X_train.columns.intersection(X_test.columns)
    X_train = X_train[common_cols]
    X_test = X_test[common_cols]

    predictions = pd.DataFrame({"player": players})

    for target in TARGET_COLUMNS:
        print(f"\n🚀 Predicting: {target}")
        model = RandomForestRegressor(random_state=42)
        model.fit(X_train, y_train[target])
        preds = model.predict(X_test)

        predictions[f"predicted_{target}"] = preds

    output_file = "qb_2025_predictions.csv"
    predictions.to_csv(output_file, index=False)
    print(f"\n✅ Prediction complete. Saved to {output_file}")

if __name__ == "__main__":
    main()
