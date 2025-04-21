import pandas as pd
import mysql.connector

# Load predictions
preds_df = pd.read_csv("qb_2025_predictions.csv")
print(preds_df.columns)

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Richie30",
    database="fantasy_football"
)
cursor = conn.cursor()
print(preds_df.columns)

# 🔁 Reset the predictions table
def reset_qb_2025_stats_table(cursor):
    cursor.execute("DROP TABLE IF EXISTS qb_2025_stats")
    cursor.execute("""
        CREATE TABLE qb_2025_stats (
            Player VARCHAR(100) PRIMARY KEY,
            Predicted_PassYards_2025 FLOAT,
            Predicted_PassTDs_2025 FLOAT,
            Predicted_RushYards_2025 FLOAT,
            Predicted_RushTDs_2025 FLOAT,
            PredictedFantasyPts_2025 FLOAT
        )
    """)
    print("✅ Recreated qb_2025_stats table.")

reset_qb_2025_stats_table(cursor)

# ✅ Insert predictions into the table
insert_query = """
    INSERT INTO qb_2025_stats (
        Player, 
        Predicted_PassYards_2025,
        Predicted_PassTDs_2025,
        Predicted_RushYards_2025,
        Predicted_RushTDs_2025,
        PredictedFantasyPts_2025
    ) VALUES (%s, %s, %s, %s, %s, %s)
"""

for _, row in preds_df.iterrows():
    cursor.execute(insert_query, (
        row['player'],
        row['predicted_pass_yards'],
        row['predicted_pass_tds'],
        row['predicted_rush_yards'],
        row['predicted_rush_tds'],
        row['predicted_fantasy_points']
    ))

conn.commit()
print("✅ Predictions successfully inserted into MySQL.")

cursor.close()
conn.close()