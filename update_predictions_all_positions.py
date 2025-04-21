import pandas as pd
import mysql.connector

def insert_into_table(df, table_name, create_stmt, insert_stmt, insert_columns):
    print(f"📤 Updating {table_name}...")
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    cursor.execute(create_stmt)
    for _, row in df.iterrows():
        cursor.execute(insert_stmt, tuple(row[col] for col in insert_columns))
    print(f"✅ Inserted into {table_name}.")


# Connect to DB
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Richie30",
    database="fantasy_football"
)
cursor = conn.cursor()

# === QB ===
qb_df = pd.read_csv("qb_2025_graded.csv").drop_duplicates(subset="player")
insert_into_table(
    qb_df,
    "qb_2025_stats",
    """
    CREATE TABLE qb_2025_stats (
        Player VARCHAR(100) PRIMARY KEY,
        Predicted_PassYards_2025 FLOAT,
        Predicted_PassTDs_2025 FLOAT,
        Predicted_RushYards_2025 FLOAT,
        Predicted_RushTDs_2025 FLOAT,
        PredictedFantasyPts_2025 FLOAT,
        FinalGrade_2025 FLOAT,
        GradeLabel_2025 VARCHAR(20)
    )
    """,
    """
    INSERT INTO qb_2025_stats VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """,
    [
        "player",
        "predicted_pass_yards",
        "predicted_pass_tds",
        "predicted_rush_yards",
        "predicted_rush_tds",
        "predicted_fantasy_points",
        "final_grade",
        "grade_label"
    ]
)


# === RB ===
rb_df = pd.read_csv("rb_2025_graded.csv").drop_duplicates(subset="player")
insert_into_table(
    rb_df,
    "rb_2025_stats",
    """
    CREATE TABLE rb_2025_stats (
        Player VARCHAR(100) PRIMARY KEY,
        Predicted_RushYards_2025 FLOAT,
        Predicted_RushTDs_2025 FLOAT,
        Predicted_RecYards_2025 FLOAT,
        Predicted_RecTDs_2025 FLOAT,
        Predicted_Receptions_2025 FLOAT,
        PredictedFantasyPts_2025 FLOAT,
        FinalGrade_2025 FLOAT,
        GradeLabel_2025 VARCHAR(20)
    )
    """,
    """
    INSERT INTO rb_2025_stats VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """,
    [
        "player",
        "predicted_rush_yds",
        "predicted_rush_tds",
        "predicted_rec_yds",
        "predicted_rec_tds",
        "predicted_receptions",
        "predicted_fantasy_points",
        "final_grade",
        "grade_label"
    ]
)


# === WR ===
wr_df = pd.read_csv("wr_2025_graded.csv").drop_duplicates(subset="player")
insert_into_table(
    wr_df,
    "wr_2025_stats",
    """
    CREATE TABLE wr_2025_stats (
        Player VARCHAR(100) PRIMARY KEY,
        Predicted_RecYards_2025 FLOAT,
        Predicted_RecTDs_2025 FLOAT,
        Predicted_Receptions_2025 FLOAT,
        PredictedFantasyPts_2025 FLOAT,
        FinalGrade_2025 FLOAT,
        GradeLabel_2025 VARCHAR(20)
    )
    """,
    """
    INSERT INTO wr_2025_stats VALUES (%s, %s, %s, %s, %s, %s, %s)
    """,
    [
        "player",
        "predicted_rec_yds",
        "predicted_rec_tds",
        "predicted_receptions",
        "predicted_fantasy_points",
        "final_grade",
        "grade_label"
    ]
)


# === TE ===
te_df = pd.read_csv("te_2025_graded.csv").drop_duplicates(subset="player")
insert_into_table(
    te_df,
    "te_2025_stats",
    """
    CREATE TABLE te_2025_stats (
        Player VARCHAR(100) PRIMARY KEY,
        Predicted_RecYards_2025 FLOAT,
        Predicted_RecTDs_2025 FLOAT,
        Predicted_Receptions_2025 FLOAT,
        PredictedFantasyPts_2025 FLOAT,
        FinalGrade_2025 FLOAT,
        GradeLabel_2025 VARCHAR(20)
    )
    """,
    """
    INSERT INTO te_2025_stats VALUES (%s, %s, %s, %s, %s, %s, %s)
    """,
    [
        "player",
        "predicted_rec_yds",
        "predicted_rec_tds",
        "predicted_receptions",
        "predicted_fantasy_points",
        "final_grade",
        "grade_label"
    ]
)


conn.commit()
cursor.close()
conn.close()
print("✅ All graded 2025 stats successfully uploaded to MySQL.")
