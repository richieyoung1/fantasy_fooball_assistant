import requests
import pandas as pd
from bs4 import BeautifulSoup, Comment
import time
import io
import datetime
import re # Import regex for cleaning player names

# --- Configuration ---
YEARS_TO_SCRAPE = 5
DELAY_BETWEEN_REQUESTS = 15 # Seconds - adjust if rate limited
BASE_URL = "https://www.pro-football-reference.com"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
}
MIN_PASS_ATTEMPTS_FOR_NON_QB_POS = 5 # Keep players with missing Pos if they have at least this many pass attempts
# --- End Configuration ---

def clean_player_name(name):
    """Removes special characters often appended to names in PFR tables."""
    if isinstance(name, str):
        return re.sub(r'[*+]$', '', name).strip()
    return name

def scrape_table(url, table_id, headers):
    """Fetches and parses a specific table from a URL, handling comments."""
    print(f"  Fetching {url}...")
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status() # Check for HTTP errors (like 404, 429)
        soup = BeautifulSoup(res.text, "html.parser")

        table_html = None
        # Try finding table within comments first
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
        for comment in comments:
            if f'id="{table_id}"' in comment:
                comment_soup = BeautifulSoup(comment, "html.parser")
                table = comment_soup.find("table", id=table_id)
                if table:
                    table_html = str(table)
                    print(f"  Found table '{table_id}' inside comments.")
                    break

        # If not found in comments, try finding directly
        if table_html is None:
            table = soup.find("table", id=table_id)
            if table:
                table_html = str(table)
                print(f"  Found table '{table_id}' directly in HTML.")
            else:
                print(f"⚠️ Table with id='{table_id}' not found at {url}.")
                return None

        # Parse HTML table using pandas
        df_list = pd.read_html(io.StringIO(table_html))
        if not df_list:
             print(f"⚠️ Pandas could not parse the table '{table_id}' from HTML.")
             return None

        df = df_list[0]

        # Handle multi-level headers - PFR often has stat names in the second level
        if isinstance(df.columns, pd.MultiIndex):
            print("  Detected multi-level header, attempting to flatten...")
            # Attempt to find the level with 'Player' or 'Tm' which usually contains the main stats
            level_to_use = 0
            for i, level in enumerate(df.columns.levels):
                if 'Player' in level or 'Tm' in level:
                    level_to_use = i
                    break
            df.columns = df.columns.get_level_values(level_to_use)
            # Handle potential duplicate column names after flattening (e.g., 'Yds')
            df.columns = make_columns_unique(df.columns)


        # Remove rows that are just header repeats within the table body
        if 'Rk' in df.columns:
             df = df[df['Rk'] != 'Rk']

        # Clean player names
        if 'Player' in df.columns:
            df['Player'] = df['Player'].apply(clean_player_name)
        else:
            print(f"⚠️ 'Player' column not found in table '{table_id}'.")
            # Attempt to find a player-like column if 'Player' is missing (heuristic)
            potential_player_cols = [col for col in df.columns if 'Player' in col or col in ['Name']]
            if potential_player_cols:
                player_col = potential_player_cols[0]
                print(f"  Using column '{player_col}' as player name.")
                df.rename(columns={player_col: 'Player'}, inplace=True)
                df['Player'] = df['Player'].apply(clean_player_name)
            else:
                 print(f"❌ Could not identify a player name column in table '{table_id}'. Skipping merge step later.")


        print(f"  Successfully parsed table '{table_id}'.")
        return df

    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error fetching {url}: {e}")
        if e.response.status_code == 429:
            print("🚨 Rate limit likely hit. Consider increasing DELAY_BETWEEN_REQUESTS.")
        return None # Indicate failure
    except requests.exceptions.RequestException as e:
        print(f"❌ Network Error fetching {url}: {e}")
        return None
    except Exception as e:
        print(f"❌ Error processing table '{table_id}' from {url}: {e}")
        # import traceback
        # traceback.print_exc() # Uncomment for detailed debug info
        return None

def make_columns_unique(columns):
    """Appends suffixes to duplicate column names."""
    seen = {}
    new_columns = []
    for col in columns:
        # Ensure col is a string before checking 'in seen'
        col_str = str(col)
        if col_str in seen:
            seen[col_str] += 1
            new_columns.append(f"{col_str}.{seen[col_str]}")
        else:
            seen[col_str] = 0
            new_columns.append(col_str) # Use the original column name if possible
    return new_columns

# --- Main Script Logic ---
current_year = datetime.datetime.now().year
# NFL season year is the previous year if current month is before ~September
# Adjust this logic if running at a different time of year or need specific seasons
last_completed_season = current_year - 1 if datetime.datetime.now().month < 9 else current_year

years = range(last_completed_season, last_completed_season - YEARS_TO_SCRAPE, -1)

print(f"🚀 Starting QB stats scrape for years: {list(years)}")

for year in years:
    print(f"\n--- Processing Year: {year} ---")
    passing_url = f"{BASE_URL}/years/{year}/passing.htm"
    rushing_url = f"{BASE_URL}/years/{year}/rushing.htm"

    # Scrape Passing Stats
    passing_df = scrape_table(passing_url, "passing", HEADERS)
    time.sleep(DELAY_BETWEEN_REQUESTS) # Delay after passing scrape

    # Scrape Rushing Stats
    rushing_df = scrape_table(rushing_url, "rushing", HEADERS)
    time.sleep(DELAY_BETWEEN_REQUESTS) # Delay after rushing scrape

    # --- Data Cleaning and Merging ---
    final_df = pd.DataFrame()

    # Define desired columns and their final names
    pass_cols_map = {
        'Player': 'Player', 'Age': 'Age', 'Tm': 'Tm', 'Pos': 'Pos', 'G': 'Games', 'GS': 'Games Started',
        'Cmp': 'Completions', 'Att': 'Pass Atts', 'Yds': 'Pass Yards', 'TD': 'Pass TDs',
        'Int': 'Interceptions', 'Rate': 'Passer Rating'
    }
    rush_cols_map = {'Player': 'Player', 'Att': 'Rush Atts', 'Yds': 'Rush Yards', 'TD': 'Rush TDs'}

    # Process Passing Data
    passing_df_processed = pd.DataFrame()
    if passing_df is not None and 'Player' in passing_df.columns:
        passing_df_processed = passing_df.copy()
        # Ensure required columns exist, find alternatives if necessary
        for original_col, final_col in pass_cols_map.items():
            if original_col not in passing_df_processed.columns:
                alt_col = next((c for c in passing_df_processed.columns if str(c).startswith(original_col)), None)
                if alt_col:
                    print(f"  Mapping passing column '{alt_col}' to '{original_col}' before rename.")
                    passing_df_processed.rename(columns={alt_col: original_col}, inplace=True)
                else:
                    print(f"  Adding missing passing column: {original_col}")
                    passing_df_processed[original_col] = pd.NA
        # Select and rename
        passing_df_processed = passing_df_processed[list(pass_cols_map.keys())].rename(columns=pass_cols_map)
        print("  Processed passing data.")
    else:
        print("⚠️ Skipping passing data processing due to previous errors or missing 'Player' column.")

    # Process Rushing Data
    rushing_df_processed = pd.DataFrame()
    if rushing_df is not None and 'Player' in rushing_df.columns:
        rushing_df_processed = rushing_df.copy()
         # Ensure required columns exist, find alternatives
        for original_col, final_col in rush_cols_map.items():
            if original_col not in rushing_df_processed.columns:
                alt_col = next((c for c in rushing_df_processed.columns if str(c).startswith(original_col)), None)
                if alt_col:
                    print(f"  Mapping rushing column '{alt_col}' to '{original_col}' before rename.")
                    rushing_df_processed.rename(columns={alt_col: original_col}, inplace=True)
                else:
                    print(f"  Adding missing rushing column: {original_col}")
                    rushing_df_processed[original_col] = pd.NA
        # Select and rename
        rushing_df_processed = rushing_df_processed[list(rush_cols_map.keys())].rename(columns=rush_cols_map)
        print("  Processed rushing data.")

    # Merge Data
    if not passing_df_processed.empty and not rushing_df_processed.empty:
        print("  Merging passing and rushing data...")
        # Use outer merge to keep all players initially
        final_df = pd.merge(passing_df_processed, rushing_df_processed, on='Player', how='outer', suffixes=('_pass', '_rush'))
    elif not passing_df_processed.empty:
        print("  Only passing data found.")
        final_df = passing_df_processed
    elif not rushing_df_processed.empty:
        print("  Only rushing data found.")
        final_df = rushing_df_processed
    else:
        print("⚠️ No passing or rushing data processed.")
        final_df = pd.DataFrame() # Ensure final_df is an empty DataFrame

    # --- Final Output ---
    if not final_df.empty:
        # Convert stat columns to numeric before filtering/filling
        numeric_cols = [
            'Age', 'Games', 'Games Started', 'Completions', 'Pass Atts', 'Pass Yards',
            'Pass TDs', 'Interceptions', 'Passer Rating', 'Rush Atts', 'Rush Yards', 'Rush TDs'
        ]
        for col in numeric_cols:
            if col in final_df.columns:
                final_df[col] = pd.to_numeric(final_df[col], errors='coerce')

        # Fill NaNs created by merge (especially for players only in one table)
        fill_values = {
            'Completions': 0, 'Pass Atts': 0, 'Pass Yards': 0, 'Pass TDs': 0, 'Interceptions': 0,
            'Passer Rating': 0.0, 'Rush Atts': 0, 'Rush Yards': 0, 'Rush TDs': 0,
            'Games': 0, 'Games Started': 0
        }
        final_df.fillna(fill_values, inplace=True)
        # Handle descriptive columns like Pos, Tm, Age - prioritize passing info if available
        for col in ['Pos', 'Tm', 'Age', 'Games', 'Games Started']:
             if f'{col}_pass' in final_df.columns: # Check if merge created duplicate cols
                 final_df[col] = final_df[f'{col}_pass'].fillna(final_df.get(f'{col}_rush')) # Use .get for rush col
                 final_df.drop(columns=[f'{col}_pass', f'{col}_rush'], errors='ignore', inplace=True)
        final_df['Pos'] = final_df['Pos'].fillna('').str.upper() # Ensure Pos is uppercase string

        # --- **Improved QB Filtering** ---
        print("  Applying QB filtering...")
        # Keep if Pos is 'QB' OR (Pos is missing/empty AND has significant Pass Atts)
        qb_condition = (final_df['Pos'] == 'QB') | \
                       ((final_df['Pos'] == '') & (final_df['Pass Atts'] >= MIN_PASS_ATTEMPTS_FOR_NON_QB_POS))
        original_count = len(final_df)
        final_df = final_df[qb_condition]
        print(f"  Filtered from {original_count} to {len(final_df)} potential QBs.")
        # --- **End Improved QB Filtering** ---

        # --- Filter Top 50 based on Passing Yards ---
        if 'Pass Yards' in final_df.columns and not final_df.empty:
            print("  Filtering top 50 QBs based on Passing Yards...")
            # Sort by Pass Yards (descending), keep top 50
            final_df = final_df.sort_values(by='Pass Yards', ascending=False, na_position='last').head(50)
            print(f"  Selected top {len(final_df)} QBs.")
        elif final_df.empty:
             print("  No QBs remained after filtering. Cannot select top 50.")
        else:
            print("⚠️ 'Pass Yards' column not found after processing. Cannot filter top 50 QBs.")
        # --- End Filter Top 50 ---

        # Define final column order
        final_cols_order = [
            'Player', 'Tm', 'Age', 'Pos', 'Games', 'Games Started',
            'Completions', 'Pass Atts', 'Pass Yards', 'Pass TDs', 'Interceptions', 'Passer Rating',
            'Rush Atts', 'Rush Yards', 'Rush TDs'
        ]
        # Only include columns that actually exist in the dataframe
        final_cols_order = [col for col in final_cols_order if col in final_df.columns]

        final_df = final_df[final_cols_order]

        # Save to CSV
        if not final_df.empty:
            output_filename = f"qb_{year}_stats.csv"
            try:
                final_df.to_csv(output_filename, index=False)
                print(f"✅ Successfully saved top QB data for {year} to {output_filename}")
            except Exception as e:
                print(f"❌ Error saving data for {year} to CSV: {e}")
        else:
             print(f"ℹ️ No QB data remained after filtering for {year}. No file saved.")
    else:
        print(f"❌ No data processed for {year}. Skipping file save.")

print("\n🏁 Multi-year QB stat scraping finished.")
