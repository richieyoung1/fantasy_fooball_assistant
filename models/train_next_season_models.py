"""Train, tune, evaluate, and save every next-season projection model."""

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV, GroupKFold

from feature_engineering import BASE_FEATURES, TARGETS, add_derived_features, model_features


PARAM_GRID = {
    "n_estimators": [100, 200],
    "learning_rate": [0.03, 0.08],
    "max_depth": [2, 3],
    "min_samples_leaf": [3, 8],
    "subsample": [0.8, 1.0],
}


def load_seasons(position, data_dir):
    frames = []
    for path in sorted(data_dir.glob(f"{position.lower()}_????_stats.csv")):
        year = int(path.stem.split("_")[1])
        frame = pd.read_csv(path)
        if "Games" not in frame and "G" in frame:
            frame = frame.rename(columns={"G": "Games"})
        frame["Season"] = year
        frames.append(frame)
    if len(frames) < 2:
        raise ValueError(f"Need at least two seasons of {position} stat files in {data_dir}")
    return pd.concat(frames, ignore_index=True)


def train_position(position, data_dir, output_dir):
    data = load_seasons(position, data_dir)
    required = set(BASE_FEATURES[position] + TARGETS[position] + ["Player", "Season"])
    missing = sorted(required - set(data.columns))
    if missing:
        raise ValueError(f"{position} data is missing columns: {', '.join(missing)}")

    for column in set(BASE_FEATURES[position] + TARGETS[position]):
        data[column] = pd.to_numeric(data[column], errors="coerce")
    data = data.sort_values(["Player", "Season"])
    next_season = data.groupby("Player")["Season"].shift(-1)
    for target in TARGETS[position]:
        shifted = data.groupby("Player")[target].shift(-1)
        data[f"{target}_NextSeason"] = shifted.where(next_season == data["Season"] + 1)

    enriched = add_derived_features(data, position)
    features = model_features(position, enriched)
    latest_target_season = int(data["Season"].max())
    metrics = []
    output_dir.mkdir(parents=True, exist_ok=True)

    for target in TARGETS[position]:
        target_column = f"{target}_NextSeason"
        usable = enriched.dropna(subset=features + [target_column]).copy()
        # Hold out the newest observed target season to simulate a real forecast.
        target_seasons = usable["Season"] + 1
        holdout_year = int(target_seasons.max())
        train = usable[target_seasons < holdout_year]
        test = usable[target_seasons == holdout_year]
        if len(train) < 20 or len(test) < 2:
            raise ValueError(f"Not enough chronological data for {position} {target}")

        groups = train["Season"]
        folds = min(3, groups.nunique())
        search = GridSearchCV(
            GradientBoostingRegressor(random_state=42), PARAM_GRID,
            scoring="neg_mean_squared_error", cv=GroupKFold(folds), n_jobs=-1,
        )
        search.fit(train[features], train[target_column], groups=groups)
        prediction = search.best_estimator_.predict(test[features])
        row = {
            "position": position, "target": target, "holdout_season": holdout_year,
            "train_rows": len(train), "test_rows": len(test),
            "mse": mean_squared_error(test[target_column], prediction),
            "mae": mean_absolute_error(test[target_column], prediction),
            "r2": r2_score(test[target_column], prediction),
            "best_parameters": json.dumps(search.best_params_, sort_keys=True),
        }
        metrics.append(row)
        print(f"{position:2} {target:15} MSE={row['mse']:10.2f} R²={row['r2']:7.3f} {row['best_parameters']}")

        # Refit the selected configuration on every known consecutive-season pair.
        model = GradientBoostingRegressor(random_state=42, **search.best_params_)
        model.fit(usable[features], usable[target_column])
        stem = f"{position.lower()}_predictive_{target.lower().replace(' ', '_')}"
        joblib.dump(model, output_dir / f"{stem}_model.pkl")
        (output_dir / f"{stem}_metadata.json").write_text(json.dumps({
            "features": features, "training_through": latest_target_season,
            "best_parameters": search.best_params_, "holdout_metrics": row,
        }, indent=2))

    return metrics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--positions", nargs="+", default=list(BASE_FEATURES), choices=BASE_FEATURES)
    parser.add_argument("--data-dir", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, default=Path("models"))
    args = parser.parse_args()
    rows = []
    for position in args.positions:
        rows.extend(train_position(position, args.data_dir, args.output_dir))
    report = args.output_dir / "model_metrics.csv"
    pd.DataFrame(rows).to_csv(report, index=False)
    print(f"\nSaved per-model metrics to {report}")


if __name__ == "__main__":
    main()
