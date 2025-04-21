import requests
import pandas as pd
from bs4 import BeautifulSoup
import os

def scrape_qb_advanced_stats(year):
    print(f"📊 Scraping advanced QB stats for {year}...")

    url = f"https://www.pro-football-reference.com/years/{year}/passing_advanced.htm"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the actual table
    table = soup.find('table', id='passing_advanced')
    if table is None:
        print(f"❌ Table not found for {year}")
        return

    # Read table using pandas
    df = pd.read_html(str(table))[0]

    # Handle multi-level headers
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(-1)

    # Save CSV
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, f'qb_advanced_{year}.csv')
    df.to_csv(output_path, index=False)
    print(f"✅ Saved: {output_path}")

if __name__ == "__main__":
    for year in range(2020, 2025):
        try:
            scrape_qb_advanced_stats(year)
        except Exception as e:
            print(f"⚠️ Failed to scrape {year}: {e}")
