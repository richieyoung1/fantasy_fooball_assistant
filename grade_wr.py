import pandas as pd
import numpy as np

def load_fantasy_history():
    dfs = []
    for year in range(2020, 2025):
        df = pd.read_csv(f"wr_{year}_stats.csv")
        df["year"] = year
        df.columns = df.columns.str.lower().str.replace(" ", "_")

        # Infer column names
        rush_yds = df.get("rush_yds", df.get("yds_rush", 0))
        rush_tds = df.get("rush_tds", df.get("td_rush", 0))
        rec_yds = df.get("rec_yds", df.get("yds", 0))   # 'yds' from receiving table
        rec_tds = df.get("rec_tds", df.get("td", 0))    # 'td' from receiving table
        receptions = df.get("receptions", df.get("rec", 0))

        df["fantasy_points"] = (
            0.1 * rec_yds +
            6 * rec_tds +
            1 * receptions +
            0.1 * rush_yds +
            6 * rush_tds
        )

        dfs.append(df[["player", "year", "fantasy_points"]])
    return pd.concat(dfs, ignore_index=True)


def compute_grades():
    print("📊 Loading WR historical stats...")
    history = load_fantasy_history()

    # Group by player
    stats_summary = history.groupby("player").agg(
        avg_fantasy=("fantasy_points", "mean"),
        std_fantasy=("fantasy_points", "std"),
        games_played=("fantasy_points", "count")
    ).reset_index()
    stats_summary["std_fantasy"] = stats_summary["std_fantasy"].fillna(0)


    # Consistency score: high = good
    stats_summary["consistency_score"] = (1 - (stats_summary["std_fantasy"] / (stats_summary["avg_fantasy"] + 1e-6))) * 100
    stats_summary["consistency_score"] = stats_summary["consistency_score"].clip(lower=0, upper=100)

    # Normalize prior stat scores
    stats_summary["prior_stat_score"] = 100 * (stats_summary["avg_fantasy"] / stats_summary["avg_fantasy"].max())

    # Load 2025 predictions
    preds = pd.read_csv("wr_2025_predictions.csv")
    preds.columns = preds.columns.str.lower().str.replace(" ", "_")

    # Normalize potential score
    preds["potential_score"] = 100 * (preds["predicted_fantasy_points"] / preds["predicted_fantasy_points"].max())

    # Merge everything
    merged = preds.merge(stats_summary, on="player", how="left")

    # Final grade
    merged["final_grade"] = (
        0.35 * merged["prior_stat_score"].fillna(0) +
        0.25 * merged["consistency_score"].fillna(50) +
        0.25 * merged["potential_score"].fillna(50) +
        0.15 * (merged["predicted_fantasy_points"] / merged["predicted_fantasy_points"].max() * 100)
    ).round(1)


    # Optional: Label tier
    def label_grade(g):
        if g >= 80: return "Elite" #6 players
        if g >= 70: return "Starter" # 20 players
        if g >= 60: return "Flex"  # 23 players
        if g >= 40: return "Depth" # 130 players
        return "Risky"

    merged["grade_label"] = merged["final_grade"].apply(label_grade)

    # Save results
    merged.to_csv("wr_2025_graded.csv", index=False)
    print("✅ Saved: wr_2025_graded.csv")

if __name__ == "__main__":
    compute_grades()
