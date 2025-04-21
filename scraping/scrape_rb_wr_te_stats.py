import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import StringIO

position = "RB"
url = "https://www.pro-football-reference.com/years/2023/rushing_advanced.htm"
print(f"📊 Scraping {position} stats from {url}...")

headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

# Grab table and use pandas
table = soup.find("table")
df = pd.read_html(StringIO(str(table)))[0]

# Drop repeated headers
df = df[df[df.columns[0]] != df.columns[0]]

# Preview column names for debugging
print(f"📋 Columns found: {list(df.columns)}")

# Try to find a working set of column names
expected_columns = ["Player", "Team", "Pos", "G", "Yds", "TD"]
actual_columns = [col for col in expected_columns if col in df.columns]

if not actual_columns:
    print("❌ Could not find expected columns. Please check website structure.")
else:
    df = df[actual_columns]
    df.to_csv("rb_2023_stats.csv", index=False)
    print("✅ Saved RB stats to rb_2023_stats.csv")
print("📊 Scraping completed!")