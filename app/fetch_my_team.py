import requests
import csv

LEAGUE_ID = "1180090606902087680"
USER_NAME = "richieyoung"  # 🔁 Replace this with your Sleeper username

# Step 1: Get all users in the league to find your user_id
users_url = f"https://api.sleeper.app/v1/league/{LEAGUE_ID}/users"
users_response = requests.get(users_url)
users = users_response.json()

user_id = None
for user in users:
    if user["display_name"].lower() == USER_NAME.lower():
        user_id = user["user_id"]
        break

if not user_id:
    print(f"❌ Could not find user '{USER_NAME}' in the league.")
    exit()

print(f"🔍 Found user ID: {user_id}")

# Step 2: Get all rosters in the league
rosters_url = f"https://api.sleeper.app/v1/league/{LEAGUE_ID}/rosters"
rosters_response = requests.get(rosters_url)
rosters = rosters_response.json()

my_players = []
for roster in rosters:
    if str(roster["owner_id"]) == str(user_id):
        my_players = roster["players"]
        break

if not my_players:
    print("❌ Could not find any players on your roster.")
    exit()

print(f"📋 Found {len(my_players)} players on your team.")

# Step 3: Get NFL player data from Sleeper
players_url = "https://api.sleeper.app/v1/players/nfl"
players_response = requests.get(players_url)
all_player_data = players_response.json()

filtered = []
for pid in my_players:
    player = all_player_data.get(pid)
    if player:
        name = player.get("full_name") or f"{player.get('first_name')} {player.get('last_name')}"
        team = player.get("team") or "FA"
        position = player.get("position") or "N/A"
        ppg = 0.0
        projected = 0.0
        rank = 0
        filtered.append([name, team, position, ppg, projected, rank])

# Step 4: Save to CSV
with open("players.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Player", "Team", "Pos", "PPG", "Proj ROS", "Rank"])
    writer.writerows(filtered)

print("✅ Your fantasy team saved to players.csv")
