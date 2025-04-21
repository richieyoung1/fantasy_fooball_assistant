import pandas as pd
import mysql.connector
import os
import glob

# --- MySQL Config ---
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Richie30",
    "database": "fantasy_football"
}

# --- Utility: Round all numeric values to 0 decimals ---
def round_numeric_columns(df):
    for col in df.select_dtypes(include='number').columns:
        df[col] = df[col].round(0).astype("Int64")  # nullable int
    return df

# --- Connect to DB ---
conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

# --- Loop through all 2025 prediction CSVs ---
csv_files = glob.glob("*_2025_predictions.csv")

for file in csv_files:
    print(f"📥 Loading: {file}")

    # Position prefix (e.g., qb, rb)
    table_prefix = file.split("_")[0]
    table_name = f"{table_prefix}_2025_stats"

    # Load and round the data
    df = pd.read_csv(file)
    df = round_numeric_columns(df)

    # Clean column names for SQL
    df.columns = [col.strip().replace(" ", "_").replace("%", "pct") for col in df.columns]

    # Drop table if exists
    cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")

    # Create table SQL
    cols_sql = []
    for col in df.columns:
        dtype = "INT" if pd.api.types.is_integer_dtype(df[col]) else "VARCHAR(255)"
        cols_sql.append(f"`{col}` {dtype}")
    create_sql = f"CREATE TABLE `{table_name}` ({', '.join(cols_sql)})"
    cursor.execute(create_sql)

    # Insert rows
    for _, row in df.iterrows():
        values = [None if pd.isna(x) else str(int(x)) if isinstance(x, (int, float)) and not isinstance(x, str) else str(x) for x in row]
        placeholders = ', '.join(['%s'] * len(values))
        insert_sql = f"INSERT INTO `{table_name}` VALUES ({placeholders})"
        cursor.execute(insert_sql, values)

    conn.commit()
    print(f"✅ Imported to {table_name} ({len(df)} rows)")

cursor.close()
conn.close()
print("🏁 All 2025 prediction files loaded.")
