import pandas as pd
import numpy as np

def label_grade(g):
    if g >= 80: return "Elite"
    if g >= 70: return "Starter"
    if g >= 60: return "Streamer"
    if g >= 40: return "Depth"
    return "Risky"

def load_qb_history():
    dfs = []
    for year in range(2020, 2025):
        df = pd.read_csv(f"qb_{year}_stats.csv")
        df.columns = df.columns.str.lower().str.replace(" ", "_")
        df["year"] = year

        df["fantasy_points"] = (
            0.04 * df["pass_yards"] +
            4 * df["pass_tds"] +
            -1 * df["interceptions"] +
            0.1 * df["rush_yards"] +
            6 * df["rush_tds"]
        )

        dfs.append(df[["player", "year", "fantasy_points"]])
    return pd.concat(dfs, ignore_index=True)

def grade_qbs():
    print("📊 Grading QBs...")
    history = load_qb_history()

    summary = history.groupby("player").agg(
        avg_fantasy=("fantasy_points", "mean"),
        std_fantasy=("fantasy_points", "std"),
        games_played=("fantasy_points", "count")
    ).reset_index()

    summary["std_fantasy"] = summary["std_fantasy"].fillna(0)
    summary["consistency_score"] = (1 - (summary["std_fantasy"] / (summary["avg_fantasy"] + 1e-6))) * 100
    summary["consistency_score"] = summary["consistency_score"].clip(0, 100)
    summary["prior_stat_score"] = 100 * (summary["avg_fantasy"] / summary["avg_fantasy"].max())

    preds = pd.read_csv("qb_2025_predictions.csv")
    preds.columns = preds.columns.str.lower().str.replace(" ", "_")

    preds["normalized_projected"] = 100 * (preds["predicted_fantasy_points"] / preds["predicted_fantasy_points"].max())
    preds["potential_score"] = preds["normalized_projected"]

    merged = preds.merge(summary, on="player", how="left")

    merged["final_grade"] = (
        0.35 * merged["prior_stat_score"].fillna(0) +
        0.25 * merged["consistency_score"].fillna(50) +
        0.25 * merged["potential_score"].fillna(50) +
        0.15 * merged["normalized_projected"]
    ).round(1)

    merged["grade_label"] = merged["final_grade"].apply(label_grade)
    merged.to_csv("qb_2025_graded.csv", index=False)
    print("✅ Saved: qb_2025_graded.csv")

if __name__ == "__main__":
    grade_qbs()
