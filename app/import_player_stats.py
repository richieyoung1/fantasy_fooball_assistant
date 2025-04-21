import os
import pandas as pd
import mysql.connector
from mysql.connector import Error

# --- CONFIGURATION ---
DATA_DIR = '.'  # Current directory
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Richie30',
    'database': 'fantasy_football'
}

# Filter the files you want to include
VALID_FILES = [
    f"{pos}_{year}_stats.csv"
    for pos in ['rb', 'qb', 'te', 'wr']
    for year in range(2020, 2025)
]

# --- DATABASE CONNECTION ---
def connect_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print("✅ Connected to MySQL")
        return conn
    except Error as e:
        print(f"❌ DB Connection failed: {e}")
        return None

# --- CREATE TABLE ---
def create_table(cursor, table_name, df):
    columns = []
    for col in df.columns:
        dtype = df[col].dtype
        if pd.api.types.is_integer_dtype(dtype):
            col_type = "INT"
        elif pd.api.types.is_float_dtype(dtype):
            col_type = "FLOAT"
        else:
            col_type = "VARCHAR(255)"
        col_clean = col.replace(" ", "_").replace("-", "_").replace("%", "pct")
        columns.append(f"`{col_clean}` {col_type}")
    
    columns_sql = ", ".join(columns)
    sql = f"CREATE TABLE IF NOT EXISTS `{table_name}` ({columns_sql});"
    cursor.execute(sql)
    print(f"📄 Table `{table_name}` created")

# --- INSERT DATA ---
def insert_data(cursor, table_name, df):
    df.columns = [c.replace(" ", "_").replace("-", "_").replace("%", "pct") for c in df.columns]
    cols = ", ".join([f"`{col}`" for col in df.columns])
    placeholders = ", ".join(["%s"] * len(df.columns))
    sql = f"INSERT INTO `{table_name}` ({cols}) VALUES ({placeholders})"

    for row in df.itertuples(index=False, name=None):
        try:
            cursor.execute(sql, row)
        except Exception as e:
            print(f"⚠️ Insert failed for {row}: {e}")

# --- MAIN SCRIPT ---
def main():
    conn = connect_db()
    if conn is None:
        return
    cursor = conn.cursor()

    for filename in os.listdir(DATA_DIR):
        if filename.lower() in VALID_FILES:
            table_name = filename.replace('.csv', '').lower()
            file_path = os.path.join(DATA_DIR, filename)
            print(f"\n📂 Processing {file_path} → Table `{table_name}`")

            try:
                df = pd.read_csv(file_path)
                df.dropna(axis=1, how='all', inplace=True)
                create_table(cursor, table_name, df)
                insert_data(cursor, table_name, df)
                conn.commit()
                print(f"✅ Finished importing `{filename}`")
            except Exception as e:
                print(f"❌ Failed to process `{filename}`: {e}")

    cursor.close()
    conn.close()
    print("\n🏁 All done.")

if __name__ == "__main__":
    main()
