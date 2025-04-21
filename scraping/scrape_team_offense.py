import requests
from bs4 import BeautifulSoup, Comment
import pandas as pd
import os
from io import StringIO

def scrape_team_offensive_stats(year):
    print(f"\n📊 Scraping team offensive stats for {year}...")

    url = f"https://www.pro-football-reference.com/years/{year}/"
    response = requests.get(url)
    if not response.ok:
        raise Exception(f"❌ Failed to load page: {url}")

    soup = BeautifulSoup(response.content, 'html.parser')

    # Look through HTML comments to find the team stats table
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))

    team_stats_table = None
    for comment in comments:
        if 'id="team_stats"' in comment:
            comment_soup = BeautifulSoup(comment, 'html.parser')
            team_stats_table = comment_soup.find('table', {'id': 'team_stats'})
            break

    if team_stats_table is None:
        raise ValueError("❌ Couldn't find team stats table in HTML comments.")

    # Convert table to DataFrame
    df = pd.read_html(StringIO(str(team_stats_table)))[0]

    # Flatten and clean column names
    df.columns = df.columns.to_flat_index()
    df.columns = ['Rk', 'Team', 'G', 'Points', 'Total Yards', 'Off Plays', 'Yards/Play', 'Turnovers',
                  'Fumbles Lost', '1st Downs', 'Cmp', 'Att', 'Pass Yards', 'Pass TD', 'Pass Int',
                  'Net Y/A', 'Pass 1stD', 'Rush Att', 'Rush Yards', 'Rush TD', 'Rush Y/A',
                  'Rush 1stD', 'Penalties', 'Penalty Yards', '1st by Pen', 'Score%', 'TO%', 'EXP']

    df = df[df['Team'] != 'League Total']  # Remove bottom summary row if present
    df = df.drop(columns=['Rk'])           # Drop ranking column

    df['Team'] = df['Team'].str.strip()

    # Make sure output directory exists
    os.makedirs("data", exist_ok=True)
    save_path = f"data/team_offense_{year}.csv"
    df.to_csv(save_path, index=False)

    print(f"✅ Saved team stats to {save_path}")

if __name__ == "__main__":
    scrape_team_offensive_stats(2024)
