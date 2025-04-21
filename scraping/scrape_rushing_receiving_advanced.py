import os
import pandas as pd
import requests
from bs4 import BeautifulSoup, Comment
from time import sleep

# Function to fetch an advanced stats table, even if it's hidden in HTML comments
def get_advanced_table(url_suffix, table_id):
    base_url = "https://www.pro-football-reference.com"
    url = f"{base_url}/years/{url_suffix}"
    print(f"🔗 Fetching: {url}")

    response = requests.get(url)
    if not response.ok:
        print(f"❌ Error fetching {url}")
        return pd.DataFrame()

    soup = BeautifulSoup(response.content, "html.parser")

    # First try to get table directly
    table = soup.find("table", {"id": table_id})
    if table:
        return pd.read_html(str(table))[0]

    # If not found, try looking in HTML comments
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        if table_id in comment:
            comment_soup = BeautifulSoup(comment, "html.parser")
            table = comment_soup.find("table", {"id": table_id})
            if table:
                return pd.read_html(str(table))[0]

    print(f"❌ Could not find table '{table_id}' in page or comments.")
    return pd.DataFrame()

# Function to scrape advanced rushing + receiving data and combine them
def scrape_combined_advanced_rushing_receiving(start_year=2020, end_year=2024):
    os.makedirs("data", exist_ok=True)

    for year in range(start_year, end_year + 1):
        print(f"\n📆 Scraping year: {year}")

        # Get each table
        rushing_df = get_advanced_table(f"{year}/rushing_advanced.htm", "rushing_advanced")
        receiving_df = get_advanced_table(f"{year}/receiving_advanced.htm", "receiving_advanced")

        # Skip year if either is missing
        if rushing_df.empty or receiving_df.empty:
            print(f"⚠️ Skipping {year} due to missing data.")
            continue

        # Standardize column names
        rushing_df.columns = [col.lower().strip().replace(" ", "_") for col in rushing_df.columns]
        receiving_df.columns = [col.lower().strip().replace(" ", "_") for col in receiving_df.columns]

        # Clean up player names (remove '*' or '+')
        rushing_df["player"] = rushing_df["player"].str.replace(r"[*+]", "", regex=True)
        receiving_df["player"] = receiving_df["player"].str.replace(r"[*+]", "", regex=True)

        # Merge on player, team, pos, age, g, gs (safest combo)
        common_keys = ["player", "team", "pos", "age", "g", "gs"]
        combined_df = pd.merge(
            rushing_df,
            receiving_df,
            how="outer",
            on=common_keys,
            suffixes=("_rush", "_rec")
        )

        # Save to CSV
        output_path = f"data/rb_wr_advanced_{year}.csv"
        combined_df.to_csv(output_path, index=False)
        print(f"✅ Saved: {output_path}")

        sleep(1)  # Delay to avoid hammering the server

if __name__ == "__main__":
    scrape_combined_advanced_rushing_receiving()
