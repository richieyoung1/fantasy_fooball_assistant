import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
YEARS = [2020, 2021, 2022, 2023, 2024]

def merge_wr_data(year):
    print(f"\n🔄 Merging WR features for {year}...")

    rush_path = os.path.join( f"rushing_advanced_{year}.csv")
    rec_path = os.path.join( f"receiving_advanced_{year}.csv")

    rush_df = pd.read_csv(rush_path)
    rec_df = pd.read_csv(rec_path)

    rush_df = rush_df[rush_df['pos'] == 'WR']
    rec_df = rec_df[rec_df['pos'] == 'WR']

    rush_df = rush_df.rename(columns=lambda x: f"rush_{x}" if x != "player" else x)
    rec_df = rec_df.rename(columns=lambda x: f"rec_{x}" if x != "player" else x)

    merged = pd.merge(rush_df, rec_df, on='player', how='outer')

    merged.drop(columns=[col for col in merged.columns if 'team' in col.lower() or 'pos' in col.lower()], inplace=True)

    output_path = os.path.join( f"wr_{year}_features.csv")
    merged.to_csv(output_path, index=False)
    print(f"✅ Saved: {output_path}")

if __name__ == "__main__":
    for year in YEARS:
        try:
            merge_wr_data(year)
        except Exception as e:
            print(f"❌ Failed to merge WR {year}: {e}")
