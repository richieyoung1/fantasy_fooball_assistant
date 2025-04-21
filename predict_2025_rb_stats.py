import pandas as pd
import os
from sklearn.ensemble import RandomForestRegressor
import numpy as np

# 🎯 Target stat columns
TARGET_COLUMNS = ["rush_yds", "rush_tds", "rec_yds", "rec_tds", "receptions", "fantasy_points"]

def load_and_merge(year, include_stats=True):
    features = pd.read_csv(f"rb_{year}_features.csv")

    if include_stats:
        stats = pd.read_csv(f"rb_{year}_stats.csv")
        for df in [stats, features]:
            df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
        df = stats.merge(features, on="player", how="inner")

        # Ensure numeric types
        for col in ["rush_yds", "rush_tds", "rec_yds", "rec_tds", "receptions"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        df["fantasy_points"] = (
            0.1 * df["rush_yds"] +
            6 * df["rush_tds"] +
            0.1 * df["rec_yds"] +
            6 * df["rec_tds"] +
            1 * df["receptions"]
        )
    else:
        features.columns = [col.strip().lower().replace(" ", "_") for col in features.columns]
        df = features.copy()

    return df

def prepare_data(df, target_columns=None):
    df.columns = [col.lower().strip().replace(" ", "_") for col in df.columns]
    X = df.select_dtypes(include=[np.number])
    y = df[target_columns] if target_columns else None
    return X, y

def main():
    print("\n🧠 Training on 2020–2024 RB data...")

    train_dfs = []
    for year in range(2020, 2025):
        df = load_and_merge(year, include_stats=True)
        train_dfs.append(df)
        print(f"✅ Loaded {year}: {df.shape}")

    train_df = pd.concat(train_dfs, ignore_index=True)
    X_train, _ = prepare_data(train_df, TARGET_COLUMNS)
    y_train = train_df[TARGET_COLUMNS]

    print("\n🔁 Predicting 2025 using 2024 features only...")
    test_df = load_and_merge(2024, include_stats=False)
    players = test_df["player"].reset_index(drop=True)
    X_test, _ = prepare_data(test_df)

    # Match features across train/test
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

    output_file = "rb_2025_predictions.csv"
    predictions.to_csv(output_file, index=False)
    print(f"\n✅ Prediction complete. Saved to {output_file}")

if __name__ == "__main__":
    main()
