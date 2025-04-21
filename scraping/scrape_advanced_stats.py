import requests
import pandas as pd
from bs4 import BeautifulSoup
import os

BASE_URL = "https://www.pro-football-reference.com"
YEARS = [2020, 2021, 2022, 2023, 2024]

TABLES = {
    "rushing": "rushing",
    "receiving": "receiving",
    "rushing_advanced": "rushing_advanced"
}

def scrape_table(year, category, table_id):
    print(f"📥 Scraping {category} for {year} from table '{table_id}'...")
    url = f"{BASE_URL}/years/{year}/{category}.htm"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    table = soup.find('table', id=table_id)
    if table is None:
        print(f"❌ Table '{table_id}' not found for {year}")
        return

    df = pd.read_html(str(table))[0]

    # Flatten multi-level headers if needed
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(-1)

    df = df[df['Player'] != 'Player']
    df = df.dropna(subset=['Player'])
    df['Player'] = df['Player'].str.replace(r'[*+]', '', regex=True).str.strip()
    df.columns = [col.lower().strip().replace(" ", "_") for col in df.columns]

    # Save file to a "data" folder one level up
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, f"{category}_advanced_{year}.csv")
    df.to_csv(output_path, index=False)
    print(f"✅ Saved: {output_path}")

def main():
    for year in YEARS:
        for category, table_id in TABLES.items():
            try:
                scrape_table(year, category, table_id)
            except Exception as e:
                print(f"⚠️ Error scraping {category} for {year}: {e}")

if __name__ == "__main__":
    main()
