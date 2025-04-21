import requests
import pandas as pd
from bs4 import BeautifulSoup, Comment
import time
import io # Import io for StringIO

# --- Add User-Agent Header ---
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
# --- End User-Agent Header ---

qb_urls = {
    "Joe Burrow": "https://www.pro-football-reference.com/players/B/BurrJo01.htm", # Corrected URL
    "Jared Goff": "https://www.pro-football-reference.com/players/G/GoffJa00.htm",
    "Baker Mayfield": "https://www.pro-football-reference.com/players/M/MayfBa00.htm",
    "Geno Smith": "https://www.pro-football-reference.com/players/S/SmitGe00.htm",
    "Sam Darnold": "https://www.pro-football-reference.com/players/D/DarnSa00.htm",
    "Lamar Jackson": "https://www.pro-football-reference.com/players/J/JackLa00.htm",
    "Patrick Mahomes": "https://www.pro-football-reference.com/players/M/MahoPa00.htm",
    "Aaron Rodgers": "https://www.pro-football-reference.com/players/R/RodgAa00.htm",
    "Justin Herbert": "https://www.pro-football-reference.com/players/H/HerbJu00.htm",
    "Brock Purdy": "https://www.pro-football-reference.com/players/P/PurdBr00.htm",
    "Kirk Cousins": "https://www.pro-football-reference.com/players/C/CousKi00.htm",
    "Russell Wilson": "https://www.pro-football-reference.com/players/W/WilsRu00.htm",
    "Tua Tagovailoa": "https://www.pro-football-reference.com/players/T/TagoTu00.htm",
    "Drew Brees": "https://www.pro-football-reference.com/players/B/BreeDr00.htm",
    "Jalen Hurts": "https://www.pro-football-reference.com/players/H/HurtJa00.htm"
}

all_rows = []

print("📊 Scraping year-by-year QB stats...")
for name, url in qb_urls.items():
    try:
        # --- Use Headers in Request ---
        res = requests.get(url, headers=headers)
        # --- End Use Headers ---
        res.raise_for_status() # Check for HTTP errors
        soup = BeautifulSoup(res.text, "html.parser")

        passing_table_html = None
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
        for comment in comments:
            if 'id="passing"' in comment:
                comment_soup = BeautifulSoup(comment, "html.parser")
                passing_table = comment_soup.find("table", id="passing")
                if passing_table:
                    passing_table_html = str(passing_table)
                    break

        if passing_table_html is None:
            passing_table = soup.find("table", id="passing")
            if passing_table:
                 passing_table_html = str(passing_table)
            else:
                print(f"⚠️ No passing table found for {name} (checked comments and direct HTML)")
                continue

        # --- Use io.StringIO for pandas warning ---
        df = pd.read_html(io.StringIO(passing_table_html))[0]
        # --- End StringIO ---

        # --- Robust Header Handling ---
        if isinstance(df.columns, pd.MultiIndex):
            # PFR often has stat names in the second level
            df.columns = df.columns.get_level_values(1)
        # --- End Header Handling ---

        # --- Check if 'Year' column exists ---
        if "Year" not in df.columns:
            print(f"⚠️ 'Year' column not found in table for {name}. Columns found: {list(df.columns)}")
            continue
        # --- End Check ---

        # Filter only year rows (check for digits possibly followed by * or +)
        df = df[df["Year"].astype(str).str.match(r'^\d{4}(\*)?(\+)?$')]
        df = df.tail(5) # last 5 seasons

        for _, row in df.iterrows():
            # Ensure year is clean (remove * or +)
            year_str = str(row["Year"]).replace('*','').replace('+','')
            all_rows.append({
                "Player": name,
                "Year": year_str,
                "Age": row.get("Age", ""),
                "Team": row.get("Tm", ""),
                "Games": row.get("G", 0),
                "Completions": row.get("Cmp", 0),
                "Attempts": row.get("Att", 0),
                "Yards": row.get("Yds", 0),
                "TD": row.get("TD", 0),
                "INT": row.get("Int", 0),
                "Cmp%": row.get("Cmp%", 0),
                "Y/A": row.get("Y/A", 0),
                "Rate": row.get("Rate", 0)
            })

        print(f"✅ Fetched {name}")
        # --- Increased Delay Further ---
        time.sleep(20)  # Increased delay to 20 seconds
        # --- End Increased Delay ---

    except requests.exceptions.RequestException as e:
        print(f"❌ HTTP Error for {name}: {e}")
        # --- Add Break on Rate Limit ---
        if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 429:
            print("🚨 Rate limit hit. Stopping script to avoid further issues.")
            break # Stop the loop if we get rate limited
        # --- End Add Break ---
    except Exception as e:
        print(f"❌ Error processing {name}: {e}")
        # Optional: print more details for debugging
        # import traceback
        # traceback.print_exc()


if all_rows:
    try:
        df = pd.DataFrame(all_rows)
        # Convert relevant columns to numeric, coercing errors
        numeric_cols = ['Age', 'Games', 'Completions', 'Attempts', 'Yards', 'TD', 'INT', 'Cmp%', 'Y/A', 'Rate']
        for col in numeric_cols:
            if col in df.columns:
                 df[col] = pd.to_numeric(df[col], errors='coerce')

        df.to_csv("qb_career_season_stats.csv", index=False)
        print("\n✅ Saved year-by-year QB stats to qb_career_season_stats.csv")
    except Exception as e:
        print(f"\n❌ Error saving data to CSV: {e}")
else:
    print("\n❌ No QB stats scraped (or script stopped early due to rate limiting).")

