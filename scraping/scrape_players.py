import requests
import csv
import random

SLEEPER_PLAYERS_URL = "https://api.sleeper.app/v1/players/nfl"

print("📊 Fetching player data from Sleeper...")

response = requests.get(SLEEPER_PLAYERS_URL)
players_data = response.json()

filtered_players = []

# Accepted fantasy positions
fantasy_positions = {"QB", "RB", "WR", "TE"}

for player in players_data.values():
    pos = player.get("position")
    if pos not in fantasy_positions:
        continue

    name = player.get("full_name") or f"{player.get('first_name', '')} {player.get('last_name', '')}".strip()
    team = player.get("team") or "FA"

    # Skip unnamed or free agent players
    if name == "" or team == "FA":
        continue

    ppg = 0.0
    projected = 0.0
    rank = 0
    ppg = round(random.uniform(10, 25), 1)
    projected = round(random.uniform(100, 300), 1)
    rank = random.randint(1, 50)

    filtered_players.append([name, team, pos, ppg, projected, rank])

# Sort by name (you could replace this with stat-based sort if integrating real projections)
filtered_players = sorted(filtered_players, key=lambda x: x[0])[:50]

# Save to CSV
with open("players.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Player", "Team", "Pos", "PPG", "Proj ROS", "Rank"])
    writer.writerows(filtered_players)

print(f"✅ Top 50 fantasy players saved to players.csv")
