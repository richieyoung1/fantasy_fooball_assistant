import requests
from bs4 import BeautifulSoup
import pandas as pd

def normalize_columns(df):
    df.columns = df.columns.droplevel(0) if isinstance(df.columns, pd.MultiIndex) else df.columns
    df.columns = [str(col).strip() for col in df.columns]
    return df

def scrape_passing_stats():
    print("📊 Scraping QB passing stats...")
    url = "https://www.pro-football-reference.com/years/2023/passing.htm"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", {"id": "passing"})
    df = pd.read_html(str(table))[0]
    df = normalize_columns(df)
    df = df[df["Player"] != "Player"]

    print("✅ Passing table columns:", df.columns.tolist())

    # Rename relevant columns
    rename_map = {
        "Tm": "Team", "G": "Games", "Cmp": "Completions", "Att": "Attempts",
        "Yds": "Yards", "TD": "Touchdowns", "Int": "Interceptions", "Rate": "Passer Rating"
    }

    df = df.rename(columns=rename_map)
    keep_cols = ["Player", "Team", "Age", "Games", "Completions", "Attempts",
                 "Yards", "Touchdowns", "Interceptions", "Passer Rating"]
    df = df[keep_cols]

    for col in keep_cols[2:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

def scrape_rushing_stats():
    print("🏃 Scraping QB rushing stats...")
    url = "https://www.pro-football-reference.com/years/2023/rushing.htm"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", {"id": "rushing"})
    df = pd.read_html(str(table))[0]
    df = normalize_columns(df)
    df = df[df["Player"] != "Player"]
    df = df[df["Pos"] == "QB"]

    print("✅ Rushing table columns:", df.columns.tolist())

    df = df.rename(columns={"Tm": "Team", "Att": "Rush Attempts", "Yds": "Rush Yards", "TD": "Rush TDs"})
    keep_cols = ["Player", "Team", "Rush Attempts", "Rush Yards", "Rush TDs"]
    df = df[keep_cols]

    for col in keep_cols[2:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

# --- Main Execution ---
passing_df = scrape_passing_stats()
rushing_df = scrape_rushing_stats()

# Merge on Player + Team
merged_df = pd.merge(passing_df, rushing_df, on=["Player", "Team"], how="left")
merged_df[["Rush Attempts", "Rush Yards", "Rush TDs"]] = merged_df[["Rush Attempts", "Rush Yards", "Rush TDs"]].fillna(0)

# Save to CSV
merged_df.to_csv("qb_2023_stats.csv", index=False)
print("✅ Saved combined passing + rushing QB stats to qb_2023_stats.csv")
