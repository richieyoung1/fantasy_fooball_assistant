import pandas as pd

# Load your main QB stats file
df = pd.read_csv("qb_2023_stats.csv")

# Rename the column if needed
if "QB Style" in df.columns:
    df.rename(columns={"QB Style": "Style"}, inplace=True)
    df.to_csv("qb_2023_stats_clustered.csv", index=False)
    print("✅ Column renamed to 'Style' and saved as qb_2023_stats_clustered.csv")
else:
    print("❌ 'QB Style' column not found. Please check the file.")
