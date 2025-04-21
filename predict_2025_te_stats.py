import pandas as pd
import os
from sklearn.ensemble import RandomForestRegressor
import numpy as np

TARGET_COLUMNS = ["rec_yds", "rec_tds", "receptions", "fantasy_points"]

def load_and_merge(year, include_stats=True):
    features = pd.read_csv(f"te_{year}_features.csv")

    if include_stats:
        stats = pd.read_csv(f"te_{year}_stats.csv")
        for df in [stats, features]:
            df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

        df = stats.merge(features, on="player", how="inner")
        for col in ["rec_yds", "rec_tds", "receptions", "rush_yds", "rush_tds"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        df["fantasy_points"] = (
            0.1 * df["rec_yds"] +
            6 * df["rec_tds"] +
            1 * df["receptions"] +
            0.1 * df["rush_yds"] +
            6 * df["rush_tds"]
        )
    else:
        features.columns = [col.strip().lower().replace(" ", "_") for col in features.columns]
        df = features.copy()

    return df

def prepare_data(df, target_columns=None):
    X = df.select_dtypes(include=[np.number])
    y = df[target_columns] if target_columns else None
    return X, y

def main():
    print("\n📊 Training TE model using 2020–2024 data...")

    all_train = []
    for year in range(2020, 2025):
        df = load_and_merge(year, include_stats=True)
        all_train.append(df)

    train_df = pd.concat(all_train, ignore_index=True)
    X_train, _ = prepare_data(train_df, TARGET_COLUMNS)
    y_train = train_df[TARGET_COLUMNS]

    print("🔮 Using 2024 features to predict 2025...")
    test_df = load_and_merge(2024, include_stats=False)
    players = test_df["player"]
    X_test, _ = prepare_data(test_df)

    common_cols = X_train.columns.intersection(X_test.columns)
    X_train = X_train[common_cols]
    X_test = X_test[common_cols]

    predictions = pd.DataFrame({"player": players})

    for target in TARGET_COLUMNS:
        print(f"🚀 Predicting TE stat: {target}")
        model = RandomForestRegressor(random_state=42)
        model.fit(X_train, y_train[target])
        preds = model.predict(X_test)
        predictions[f"predicted_{target}"] = preds

    predictions.to_csv("te_2025_predictions.csv", index=False)
    print("✅ TE 2025 predictions saved to te_2025_predictions.csv")

if __name__ == "__main__":
    main()
