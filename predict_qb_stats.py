import pandas as pd
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
from math import sqrt

# 🧠 Target stats
TARGET_COLUMNS = ["pass_yards", "pass_tds", "rush_yards", "rush_tds", "fantasy_points"]

START_YEAR = 2020
END_YEAR = 2024  # Will predict up to 2023 using 2022 data

def load_and_merge(year):
    stats = pd.read_csv(f"qb_{year}_stats.csv")
    features = pd.read_csv(f"qb_{year}_features.csv")
    advanced = pd.read_csv(f"qb_advanced_{year}.csv")

    print(f"\n✅ Loaded {year} data:")
    print(f"  - stats: {stats.shape}")
    print(f"  - features: {features.shape}")
    print(f"  - advanced: {advanced.shape}")

    for df in [stats, features, advanced]:
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

    for df in [stats, features, advanced]:
        if "player" not in df.columns:
            raise ValueError("Missing 'player' column in one of the datasets")

    df = stats.merge(features, on="player", how="inner").merge(advanced, on="player", how="inner")

    required_cols = ["pass_yards", "pass_tds", "interceptions", "rush_yards", "rush_tds"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["fantasy_points"] = (
        0.04 * df["pass_yards"] +
        4 * df["pass_tds"] +
        -1 * df["interceptions"] +
        0.1 * df["rush_yards"] +
        6 * df["rush_tds"]
    )

    return df

def prepare_data(df, target_columns):
    df.columns = [col.lower().strip().replace(" ", "_") for col in df.columns]
    df.dropna(subset=target_columns, inplace=True)

    y = df[target_columns].copy()
    X = df.select_dtypes(include=[np.number]).drop(columns=target_columns, errors='ignore')

    return X, y

def main():
    for year in range(START_YEAR, END_YEAR):
        print(f"\n🧪 Training on {year}, predicting {year + 1}")

        try:
            train_df = load_and_merge(year)
            test_df = load_and_merge(year + 1)

            X_train, y_train = prepare_data(train_df, TARGET_COLUMNS)
            X_test, y_test = prepare_data(test_df, TARGET_COLUMNS)
            players = test_df["player"].reset_index(drop=True)
        except Exception as e:
            print(f"❌ Skipping {year}->{year+1} due to error: {e}")
            continue

        print(f"📊 Training shape: {X_train.shape}, Test shape: {X_test.shape}")

        results = pd.DataFrame({"player": players})

        for target in TARGET_COLUMNS:
            print(f"\n🚀 Predicting: {target}")
            model = RandomForestRegressor(random_state=42)
            model.fit(X_train, y_train[target])
            preds = model.predict(X_test)

            mae = mean_absolute_error(y_test[target], preds)
            rmse = sqrt(mean_squared_error(y_test[target], preds))

            print(f"  MAE:  {mae:.2f}")
            print(f"  RMSE: {rmse:.2f}")

            results[f"predicted_{target}"] = preds
            results[f"actual_{target}"] = y_test[target].values

        # 💾 Save results
        output_file = f"predictions_{year+1}.csv"
        results.to_csv(output_file, index=False)
        print(f"📁 Saved: {output_file}")

if __name__ == "__main__":
    main()
