import pandas as pd
import numpy as np

POSITION_CONFIG = {
    "rb": {
        "stats_file": "rb_{year}_stats.csv",
        "predictions_file": "rb_2025_predictions.csv",
        "output_file": "rb_2025_graded.csv",
        "fantasy_formula": lambda df: (
            0.1 * df.get("rec_yds", 0) +
            6 * df.get("rec_tds", 0) +
            1 * df.get("receptions", 0) +
            0.1 * df.get("rush_yds", 0) +
            6 * df.get("rush_tds", 0)
        )
    },
    "te": {
        "stats_file": "te_{year}_stats.csv",
        "predictions_file": "te_2025_predictions.csv",
        "output_file": "te_2025_graded.csv",
        "fantasy_formula": lambda df: (
            0.1 * df.get("rec_yds", 0) +
            6 * df.get("rec_tds", 0) +
            1 * df.get("receptions", 0) +
            0.1 * df.get("rush_yds", 0) +
            6 * df.get("rush_tds", 0)
        )
    }
}

def label_grade(g):
    if g >= 80: return "Elite"
    if g >= 70: return "Starter"
    if g >= 60: return "Flex"
    if g >= 40: return "Depth"
    return "Risky"

def load_history(pos_key):
    dfs = []
    config = POSITION_CONFIG[pos_key]
    for year in range(2020, 2025):
        df = pd.read_csv(config["stats_file"].format(year=year))
        df.columns = df.columns.str.lower().str.replace(" ", "_")
        df["year"] = year

        df["fantasy_points"] = config["fantasy_formula"](df)
        dfs.append(df[["player", "year", "fantasy_points"]])
    return pd.concat(dfs, ignore_index=True)

def grade_position(pos_key):
    print(f"\n📊 Grading {pos_key.upper()}s...")
    config = POSITION_CONFIG[pos_key]

    history = load_history(pos_key)
    summary = history.groupby("player").agg(
        avg_fantasy=("fantasy_points", "mean"),
        std_fantasy=("fantasy_points", "std"),
        games_played=("fantasy_points", "count")
    ).reset_index()

    summary["std_fantasy"] = summary["std_fantasy"].fillna(0)
    summary["consistency_score"] = (1 - (summary["std_fantasy"] / (summary["avg_fantasy"] + 1e-6))) * 100
    summary["consistency_score"] = summary["consistency_score"].clip(0, 100)
    summary["prior_stat_score"] = 100 * (summary["avg_fantasy"] / summary["avg_fantasy"].max())

    preds = pd.read_csv(config["predictions_file"])
    preds.columns = preds.columns.str.lower().str.replace(" ", "_")

    preds["normalized_projected"] = 100 * (preds["predicted_fantasy_points"] / preds["predicted_fantasy_points"].max())
    preds["potential_score"] = preds["normalized_projected"]  # for simplicity here

    merged = preds.merge(summary, on="player", how="left")

    merged["final_grade"] = (
        0.35 * merged["prior_stat_score"].fillna(0) +
        0.25 * merged["consistency_score"].fillna(50) +
        0.25 * merged["potential_score"].fillna(50) +
        0.15 * merged["normalized_projected"]
    ).round(1)

    merged["grade_label"] = merged["final_grade"].apply(label_grade)

    merged.to_csv(config["output_file"], index=False)
    print(f"✅ Saved: {config['output_file']}")

if __name__ == "__main__":
    grade_position("rb")
    grade_position("te")
