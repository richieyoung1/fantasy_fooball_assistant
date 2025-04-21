import pandas as pd
import requests
from bs4 import BeautifulSoup

def scrape_fantasypros_2023(position):
    url = f"https://www.fantasypros.com/nfl/stats/{position}.php?year=2023"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    table = soup.find("table", {"id": "data"})
    if not table:
        print(f"❌ Could not find table for {position.upper()}")
        return []

    players = []
    for row in table.find("tbody").find_all("tr"):
        cols = row.find_all("td")
        if len(cols) < 5:
            continue

        name = cols[0].text.strip()
        team_pos = cols[1].text.strip()
        team = team_pos.split(" - ")[0] if " - " in team_pos else ""
        games = cols[2].text.strip()
        fpts = cols[3].text.strip().replace(",", "")
        ppg = cols[4].text.strip().replace(",", "")

        try:
            players.append([
                name,
                team,
                position.upper(),
                int(games),
                float(fpts),
                float(ppg)
            ])
        except ValueError:
            continue

    return players

# Collect all positions
positions = ["qb", "rb", "wr", "te"]
all_players = []

for pos in positions:
    print(f"📊 Scraping {pos.upper()} stats from FantasyPros...")
    all_players += scrape_fantasypros_2023(pos)

# Save results
columns = ["Player", "Team", "Position", "Games", "2023 FPTS", "2023 PPG"]
df = pd.DataFrame(all_players, columns=columns)
df.to_csv("season_stats_2023.csv", index=False)
print("✅ Saved 2023 stats to season_stats_2023.csv")
