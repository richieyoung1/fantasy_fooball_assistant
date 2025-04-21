import requests
import pandas as pd
from bs4 import BeautifulSoup, Comment
import time
import io
import datetime
import re
import os

# --- Configuration ---
YEARS_TO_SCRAPE = 5
DELAY_BETWEEN_REQUESTS = 15 # Seconds
BASE_URL = "https://www.pro-football-reference.com"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
}
POSITIONS_TO_KEEP = {
    'WR': 75, # Keep top 75 WRs by total yards
    'RB': 50, # Keep top 50 RBs by total yards
    'TE': 30  # Keep top 30 TEs by total yards
}
OUTPUT_DIR = "." # Save files in the current directory
# --- End Configuration ---

def clean_player_name(name):
    """Removes special characters often appended to names in PFR tables."""
    if isinstance(name, str):
        return re.sub(r'[*+]$', '', name).strip()
    return name

def make_columns_unique(columns):
    """Appends suffixes to duplicate column names."""
    seen = {}
    new_columns = []
    for col in columns:
        col_str = str(col)
        if col_str in seen:
            seen[col_str] += 1
            new_columns.append(f"{col_str}.{seen[col_str]}")
        else:
            seen[col_str] = 0
            new_columns.append(col_str)
    return new_columns

def scrape_table(url, table_id, headers):
    """Fetches and parses a specific table from a URL, handling comments."""
    print(f"  Fetching {url}...")
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        table_html = None
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
        for comment in comments:
            if f'id="{table_id}"' in comment:
                comment_soup = BeautifulSoup(comment, "html.parser")
                table = comment_soup.find("table", id=table_id)
                if table:
                    table_html = str(table)
                    print(f"  Found table '{table_id}' inside comments.")
                    break
        if table_html is None:
            table = soup.find("table", id=table_id)
            if table:
                table_html = str(table)
                print(f"  Found table '{table_id}' directly in HTML.")
            else:
                print(f"⚠️ Table with id='{table_id}' not found at {url}.")
                return None
        df_list = pd.read_html(io.StringIO(table_html))
        if not df_list:
             print(f"⚠️ Pandas could not parse the table '{table_id}' from HTML.")
             return None
        df = df_list[0]
        if isinstance(df.columns, pd.MultiIndex):
            print("  Detected multi-level header, attempting to flatten...")
            level_to_use = 0
            for i, level in enumerate(df.columns.levels):
                if 'Player' in level or 'Tm' in level: level_to_use = i; break
            df.columns = df.columns.get_level_values(level_to_use)
            df.columns = make_columns_unique(df.columns)
        if 'Rk' in df.columns: df = df[df['Rk'] != 'Rk']
        player_col = 'Player'
        if 'Player' not in df.columns:
            potential_player_cols = [col for col in df.columns if 'Player' in col or col in ['Name']]
            if potential_player_cols:
                player_col = potential_player_cols[0]
                print(f"  Using column '{player_col}' as player name.")
                df.rename(columns={player_col: 'Player'}, inplace=True)
            else:
                 print(f"❌ Could not identify a player name column in table '{table_id}'.")
                 return df # Return df anyway, merge might fail later
        df['Player'] = df['Player'].apply(clean_player_name)
        print(f"  Successfully parsed table '{table_id}'.")
        return df
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error fetching {url}: {e}")
        if e.response.status_code == 429: print("🚨 Rate limit likely hit.")
        return None
    except Exception as e:
        print(f"❌ Error processing table '{table_id}' from {url}: {e}")
        return None

# --- Main Script Logic ---
current_year = datetime.datetime.now().year
last_completed_season = current_year - 1 if datetime.datetime.now().month < 9 else current_year
years = range(last_completed_season, last_completed_season - YEARS_TO_SCRAPE, -1)

print(f"🚀 Starting Skill Position stats scrape for years: {list(years)}")
os.makedirs(OUTPUT_DIR, exist_ok=True)

for year in years:
    print(f"\n--- Processing Year: {year} ---")
    rushing_url = f"{BASE_URL}/years/{year}/rushing.htm"
    receiving_url = f"{BASE_URL}/years/{year}/receiving.htm"

    # Scrape Rushing Stats
    rushing_df = scrape_table(rushing_url, "rushing", HEADERS)
    time.sleep(DELAY_BETWEEN_REQUESTS)

    # Scrape Receiving Stats
    receiving_df = scrape_table(receiving_url, "receiving", HEADERS)
    time.sleep(DELAY_BETWEEN_REQUESTS)

    # --- Data Cleaning and Merging ---
    if rushing_df is None and receiving_df is None:
        print(f"❌ No rushing or receiving data found for {year}. Skipping.")
        continue

    # Select relevant columns and rename for clarity before merge
    rush_cols = {'Player', 'Age', 'Tm', 'Pos', 'G', 'GS', 'Att', 'Yds', 'TD', 'Fmb'}
    rec_cols = {'Player', 'Age', 'Tm', 'Pos', 'G', 'GS', 'Tgt', 'Rec', 'Yds', 'TD', 'Fmb'}

    if rushing_df is not None:
        rushing_df = rushing_df[[col for col in rush_cols if col in rushing_df.columns]].copy()
        rushing_df.rename(columns={'Att': 'Rush Atts', 'Yds': 'Rush Yards', 'TD': 'Rush TDs', 'Fmb': 'Rush Fmb'}, inplace=True)
        # Ensure numeric types
        for col in ['Age', 'G', 'GS', 'Rush Atts', 'Rush Yards', 'Rush TDs', 'Rush Fmb']:
            if col in rushing_df.columns: rushing_df[col] = pd.to_numeric(rushing_df[col], errors='coerce')

    if receiving_df is not None:
        receiving_df = receiving_df[[col for col in rec_cols if col in receiving_df.columns]].copy()
        receiving_df.rename(columns={'Tgt': 'Targets', 'Rec': 'Receptions', 'Yds': 'Rec Yards', 'TD': 'Rec TDs', 'Fmb': 'Rec Fmb'}, inplace=True)
        # Ensure numeric types
        for col in ['Age', 'G', 'GS', 'Targets', 'Receptions', 'Rec Yards', 'Rec TDs', 'Rec Fmb']:
             if col in receiving_df.columns: receiving_df[col] = pd.to_numeric(receiving_df[col], errors='coerce')

    # Merge rushing and receiving
    if rushing_df is not None and receiving_df is not None:
        merged_df = pd.merge(rushing_df, receiving_df, on='Player', how='outer', suffixes=('_rush', '_rec'))
        # Consolidate common columns (Age, Tm, Pos, G, GS) - prioritize receiving table info if conflict
        for col in ['Age', 'Tm', 'Pos', 'G', 'GS']:
            if f'{col}_rec' in merged_df.columns and f'{col}_rush' in merged_df.columns:
                merged_df[col] = merged_df[f'{col}_rec'].fillna(merged_df[f'{col}_rush'])
                merged_df.drop(columns=[f'{col}_rec', f'{col}_rush'], inplace=True)
            elif f'{col}_rec' in merged_df.columns:
                 merged_df.rename(columns={f'{col}_rec': col}, inplace=True)
            elif f'{col}_rush' in merged_df.columns:
                 merged_df.rename(columns={f'{col}_rush': col}, inplace=True)
    elif rushing_df is not None:
        merged_df = rushing_df
    elif receiving_df is not None:
        merged_df = receiving_df
    else: # Should not happen based on earlier check, but for safety
        continue

    # Fill NaN stats with 0 after merge
    stat_cols_to_fill = ['Rush Atts', 'Rush Yards', 'Rush TDs', 'Rush Fmb',
                         'Targets', 'Receptions', 'Rec Yards', 'Rec TDs', 'Rec Fmb',
                         'G', 'GS']
    for col in stat_cols_to_fill:
        if col in merged_df.columns:
            merged_df[col] = merged_df[col].fillna(0)

    # Calculate Total Yards for sorting
    merged_df['Total Yards'] = merged_df.get('Rush Yards', 0) + merged_df.get('Rec Yards', 0)

    # --- Filter by Position and Save ---
    for pos, top_n in POSITIONS_TO_KEEP.items():
        print(f"  Filtering for top {top_n} {pos}...")
        if 'Pos' not in merged_df.columns:
            print(f"  ⚠️ 'Pos' column missing, cannot filter for {pos}.")
            continue

        # Filter for the specific position (case-insensitive)
        pos_df = merged_df[merged_df['Pos'].str.upper() == pos].copy()

        if pos_df.empty:
            print(f"  No players found for position {pos}.")
            continue

        # Sort by Total Yards and take top N
        pos_df = pos_df.sort_values(by='Total Yards', ascending=False, na_position='last').head(top_n)

        # Define final columns for output (adjust as needed)
        final_cols_order = [
            'Player', 'Tm', 'Age', 'Pos', 'G', 'GS',
            'Rush Atts', 'Rush Yards', 'Rush TDs', 'Rush Fmb',
            'Targets', 'Receptions', 'Rec Yards', 'Rec TDs', 'Rec Fmb'
        ]
        # Only include columns that actually exist in the dataframe
        final_cols_order = [col for col in final_cols_order if col in pos_df.columns]
        pos_df = pos_df[final_cols_order]

        # Save to CSV
        output_filename = os.path.join(OUTPUT_DIR, f"{pos.lower()}_{year}_stats.csv")
        try:
            pos_df.to_csv(output_filename, index=False)
            print(f"  ✅ Saved top {len(pos_df)} {pos} for {year} to {output_filename}")
        except Exception as e:
            print(f"  ❌ Error saving data for {pos} {year} to CSV: {e}")

print("\n🏁 Skill Position stat scraping finished.")
