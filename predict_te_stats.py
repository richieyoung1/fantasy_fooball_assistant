import pandas as pd
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
from math import sqrt

TARGET_COLUMNS = ["rec_yds", "rec_tds", "receptions", "fantasy_points"]
START_YEAR = 2020
END_YEAR = 2024

def load_and_merge(year):
    stats = pd.read_csv(f"te_{year}_stats.csv")
    features = pd.read_csv(f"te_{year}_features.csv")

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

    return df

def prepare_data(df):
    y = df[TARGET_COLUMNS].copy()
    X = df.select_dtypes(include=[np.number]).drop(columns=TARGET_COLUMNS, errors='ignore')
    return X, y

def main():
    for year in range(START_YEAR, END_YEAR):
        print(f"\n🧪 TE: Training on {year}, predicting {year + 1}")
        try:
            train_df = load_and_merge(year)
            test_df = load_and_merge(year + 1)

            X_train, y_train = prepare_data(train_df)
            X_test, y_test = prepare_data(test_df)
            players = test_df["player"].reset_index(drop=True)
        except Exception as e:
            print(f"❌ Skipping TE {year}->{year+1}: {e}")
            continue

        results = pd.DataFrame({"player": players})

        for target in TARGET_COLUMNS:
            print(f"🚀 Predicting TE stat: {target}")
            model = RandomForestRegressor(random_state=42)
            model.fit(X_train, y_train[target])
            preds = model.predict(X_test)

            results[f"predicted_{target}"] = preds
            results[f"actual_{target}"] = y_test[target].values

        results.to_csv(f"te_predictions_{year+1}.csv", index=False)
        print(f"✅ Saved TE predictions to te_predictions_{year+1}.csv")

if __name__ == "__main__":
    main()
