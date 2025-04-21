import requests
import pandas as pd
import json
import os
from fuzzywuzzy import process

# --- CONFIG ---
CSV_FILES = [
    f"{pos}_{year}_stats.csv"
    for pos in ['qb', 'rb', 'wr', 'te']
    for year in range(2020, 2025)
]
IMAGE_FOLDER = "images"
ESPN_API_URL = "https://sports.core.api.espn.com/v3/sports/football/nfl/athletes?limit=20000"
MATCH_THRESHOLD = 90

os.makedirs(IMAGE_FOLDER, exist_ok=True)

# --- STEP 1: Download ESPN NFL Players ---
print("📦 Downloading ESPN NFL player data...")
try:
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(ESPN_API_URL, headers=headers)
    resp.raise_for_status()
    all_players = resp.json().get("items", [])
except Exception as e:
    print(f"❌ Failed to download ESPN data: {e}")
    exit(1)

# Filter and normalize ESPN data
espn_players = []
for p in all_players:
    if p.get("firstName") and p.get("lastName") and "id" in p:
        full = f"{p['firstName']} {p['lastName']}"
        espn_players.append({
            "fullName": full,
            "id": p["id"]
        })

print(f"✅ Found {len(espn_players)} ESPN players with IDs")

# --- STEP 2: Extract unique player names from your CSVs ---
print("🧠 Scanning your player CSVs...")
unique_names = set()

for file in CSV_FILES:
    if not os.path.exists(file):
        continue
    df = pd.read_csv(file)
    if 'Player' not in df.columns:
        continue
    for name in df['Player'].dropna():
        unique_names.add(name.strip())

print(f"🔍 Found {len(unique_names)} unique names in your CSVs")

# --- STEP 3: Match names + download headshots ---
def get_espn_id(name, espn_data):
    names = [p['fullName'] for p in espn_data]
    match, score = process.extractOne(name, names)
    if score >= MATCH_THRESHOLD:
        return next(p['id'] for p in espn_data if p['fullName'] == match)
    return None

def download_headshot(player_id, filename):
    url = f"https://a.espncdn.com/i/headshots/nfl/players/full/{player_id}.png"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        with open(filename, "wb") as f:
            f.write(resp.content)
        return True
    except:
        return False

downloaded = 0

for name in sorted(unique_names):
    safe_name = name.lower().replace(" ", "_").replace(".", "").replace("'", "")
    file_path = os.path.join(IMAGE_FOLDER, f"{safe_name}.png")
    if os.path.exists(file_path):
        continue

    espn_id = get_espn_id(name, espn_players)
    if not espn_id:
        print(f"❌ No ESPN ID for: {name}")
        continue

    if download_headshot(espn_id, file_path):
        print(f"📸 Downloaded: {name} → {file_path}")
        downloaded += 1
    else:
        print(f"❌ Failed to download image for {name}")

print(f"\n✅ Done. {downloaded} headshots saved to /{IMAGE_FOLDER}")
