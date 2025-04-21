import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
YEARS = [2020, 2021, 2022, 2023, 2024]

def merge_rb_data(year):
    print(f"\n🔄 Merging RB features for {year}...")

    rush_path = os.path.join(f"rushing_advanced_{year}.csv")
    rec_path = os.path.join( f"receiving_advanced_{year}.csv")

    # Load both datasets
    rush_df = pd.read_csv(rush_path)
    rec_df = pd.read_csv(rec_path)

    # Optional: filter to RBs only (if using mixed-position source)
    rush_df = rush_df[rush_df['pos'] == 'RB']
    rec_df = rec_df[rec_df['pos'] == 'RB']

    # Clean column names for clarity before merge
    rec_df = rec_df.rename(columns=lambda x: f"rec_{x}" if x not in ['player'] else x)
    rush_df = rush_df.rename(columns=lambda x: f"rush_{x}" if x not in ['player'] else x)

    # Merge
    merged = pd.merge(rush_df, rec_df, on='player', how='outer')

    # Drop duplicate team/position info if needed
    merged.drop(columns=[col for col in merged.columns if 'team' in col.lower() or 'pos' in col.lower()], inplace=True)

    # Save
    output_path = os.path.join( f"rb_{year}_features.csv")
    merged.to_csv(output_path, index=False)
    print(f"✅ Saved: {output_path} — {merged.shape[0]} players")

if __name__ == "__main__":
    for year in YEARS:
        try:
            merge_rb_data(year)
        except Exception as e:
            print(f"❌ Failed to merge {year}: {e}")
