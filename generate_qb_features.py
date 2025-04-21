import pandas as pd
import os

def engineer_features_for_year(year):
    print(f"\n📊 Engineering features for {year}...")

    in_path = f"data/qb_{year}_stats.csv"
    out_path = f"data/qb_{year}_features.csv"

    if not os.path.exists(in_path):
        print(f"❌ Skipping: {in_path} not found.")
        return

    df = pd.read_csv(in_path)

    # Add engineered features
    df['Games Missed'] = 17 - df['Games']
    df['Touches'] = df['Pass Atts'] + df['Rush Atts']
    df['Touches Per Game'] = df['Touches'] / df['Games'].replace(0, 1)  # Avoid divide by 0

    # Round all values to whole numbers
    df = df.round(0)

    # Keep only relevant columns
    features = df[['Player', 'Games Missed', 'Touches Per Game']]

    # Save
    features.to_csv(out_path, index=False)
    print(f"✅ Saved features to {out_path}")

# --- Main ---
for y in range(2020, 2025):
    engineer_features_for_year(y)
