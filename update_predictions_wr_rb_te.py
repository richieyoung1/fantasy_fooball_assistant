import pandas as pd
import mysql.connector

# ✅ Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Richie30",
    database="fantasy_football"
)
cursor = conn.cursor()

# === WR ===
wr_df = pd.read_csv("wr_2025_predictions.csv")
wr_df = wr_df.drop_duplicates(subset="player")

cursor.execute("DROP TABLE IF EXISTS wr_2025_stats")
cursor.execute("""
    CREATE TABLE wr_2025_stats (
        Player VARCHAR(100) PRIMARY KEY,
        Predicted_RecYards_2025 FLOAT,
        Predicted_RecTDs_2025 FLOAT,
        Predicted_Receptions_2025 FLOAT,
        PredictedFantasyPts_2025 FLOAT
    )
""")
wr_query = """
    INSERT INTO wr_2025_stats (
        Player,
        Predicted_RecYards_2025,
        Predicted_RecTDs_2025,
        Predicted_Receptions_2025,
        PredictedFantasyPts_2025
    ) VALUES (%s, %s, %s, %s, %s)
"""
for _, row in wr_df.iterrows():
    cursor.execute(wr_query, (
        row["player"],
        row["predicted_rec_yds"],
        row["predicted_rec_tds"],
        row["predicted_receptions"],
        row["predicted_fantasy_points"]
    ))
print("✅ WR 2025 predictions inserted.")

# === RB ===
rb_df = pd.read_csv("rb_2025_predictions.csv")
rb_df = rb_df.drop_duplicates(subset="player")
cursor.execute("DROP TABLE IF EXISTS rb_2025_stats")
cursor.execute("""
    CREATE TABLE rb_2025_stats (
        Player VARCHAR(100) PRIMARY KEY,
        Predicted_RushYards_2025 FLOAT,
        Predicted_RushTDs_2025 FLOAT,
        Predicted_RecYards_2025 FLOAT,
        Predicted_RecTDs_2025 FLOAT,
        Predicted_Receptions_2025 FLOAT,
        PredictedFantasyPts_2025 FLOAT
    )
""")
rb_query = """
    INSERT INTO rb_2025_stats (
        Player,
        Predicted_RushYards_2025,
        Predicted_RushTDs_2025,
        Predicted_RecYards_2025,
        Predicted_RecTDs_2025,
        Predicted_Receptions_2025,
        PredictedFantasyPts_2025
    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
"""  # ✅ 7 placeholders for 7 columns

for _, row in rb_df.iterrows():
    cursor.execute(rb_query, (
        row["player"],
        row["predicted_rush_yds"],
        row["predicted_rush_tds"],
        row["predicted_rec_yds"],
        row["predicted_rec_tds"],
        row["predicted_receptions"],
        row["predicted_fantasy_points"]
    ))
print("✅ RB 2025 predictions inserted.")

# === TE ===
te_df = pd.read_csv("te_2025_predictions.csv")
te_df = te_df.drop_duplicates(subset="player")
cursor.execute("DROP TABLE IF EXISTS te_2025_stats")
cursor.execute("""
    CREATE TABLE te_2025_stats (
        Player VARCHAR(100) PRIMARY KEY,
        Predicted_RecYards_2025 FLOAT,
        Predicted_RecTDs_2025 FLOAT,
        Predicted_Receptions_2025 FLOAT,
        PredictedFantasyPts_2025 FLOAT
    )
""")
te_query = """
    INSERT INTO te_2025_stats (
        Player,
        Predicted_RecYards_2025,
        Predicted_RecTDs_2025,
        Predicted_Receptions_2025,
        PredictedFantasyPts_2025
    ) VALUES (%s, %s, %s, %s, %s)
"""

for _, row in te_df.iterrows():
    cursor.execute(te_query, (
    row["player"],
    row["predicted_rec_yds"],
    row["predicted_rec_tds"],
    row["predicted_receptions"],
    row["predicted_fantasy_points"]
))

print("✅ TE 2025 predictions inserted.")

# ✅ Commit and close
conn.commit()
cursor.close()
conn.close()
print("✅ All predictions updated in MySQL.")
