import pandas as pd
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
from math import sqrt

# 🎯 Target stats
TARGET_COLUMNS = [
    "rush_yds", "rush_tds",
    "rec_yds", "rec_tds",
    "receptions", "fantasy_points"
]

START_YEAR = 2020
END_YEAR = 2024  # will predict up to 2023 using 2022 data

def load_and_merge(year):
    stats = pd.read_csv(f"rb_{year}_stats.csv")
    features = pd.read_csv(f"rb_{year}_features.csv")

    print(f"\n✅ Loaded {year} data:")
    print(f"  - stats: {stats.shape}")
    print(f"  - features: {features.shape}")

    for df in [stats, features]:
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

    for df in [stats, features]:
        if "player" not in df.columns:
            raise ValueError("Missing 'player' column in one of the datasets")

    df = stats.merge(features, on="player", how="inner")

    # Ensure numeric + fill
    for col in ["rush_yds", "rush_tds", "rec_yds", "rec_tds", "receptions"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # 💡 Calculate fantasy points
    df["fantasy_points"] = (
        0.1 * df["rush_yds"] +
        6 * df["rush_tds"] +
        0.1 * df["rec_yds"] +
        6 * df["rec_tds"] +
        1 * df["receptions"]
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

        output_file = f"rb_predictions_{year+1}.csv"
        results.to_csv(output_file, index=False)
        print(f"📁 Saved: {output_file}")

if __name__ == "__main__":
    main()
