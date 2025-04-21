import requests
import json

def fetch_espn_player_data():
    url = "https://sports.core.api.espn.com/v3/sports/football/nfl/athletes?limit=20000"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    
    players = []
    for player in data.get('items', []):
        player_info = {
            "id": player.get("id"),
            "firstName": player.get("firstName"),
            "lastName": player.get("lastName"),
            "fullName": f"{player.get('firstName', '')} {player.get('lastName', '')}".strip(),
            "headshot": player.get("headshot", {}).get("href")
        }
        players.append(player_info)
    
    with open("espn_players.json", "w") as f:
        json.dump(players, f, indent=2)

if __name__ == "__main__":
    fetch_espn_player_data()
