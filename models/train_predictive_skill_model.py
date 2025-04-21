import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import glob
import os
import numpy as np

# --- Configuration ---
# !!! CHANGE THIS FOR EACH POSITION (WR, RB, TE) !!!
POSITION_TO_TRAIN = 'RB' # Options: 'WR', 'RB', 'TE'
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

YEARS_TO_LOAD = [2020, 2021, 2022, 2023, 2024]
MODEL_OUTPUT_DIR = "models"

# Fantasy Point Calculation Rules (Standard Non-PPR)
FPTS_YARD = 0.1  # Rushing or Receiving
FPTS_TD = 6    # Rushing or Receiving
# Add other rules if needed (e.g., FPTS_RECEPTION = 0.5 for Half-PPR)

# --- Position Specific Settings ---
if POSITION_TO_TRAIN == 'WR':
    FEATURES_SEASON_N = ['Age', 'Games', 'GS', 'Targets', 'Receptions', 'Rec Yards', 'Rec TDs']
    TARGET_STATS_SEASON_N_PLUS_1 = ['Rec Yards', 'Rec TDs', 'Receptions', 'Games'] # Predict Rec, Yards, TDs, Games
elif POSITION_TO_TRAIN == 'RB':
    FEATURES_SEASON_N = ['Age', 'Games', 'GS', 'Rush Atts', 'Rush Yards', 'Rush TDs', 'Targets', 'Receptions', 'Rec Yards', 'Rec TDs']
    TARGET_STATS_SEASON_N_PLUS_1 = ['Rush Yards', 'Rush TDs', 'Rec Yards', 'Rec TDs', 'Receptions', 'Games'] # Predict Rush/Rec Yds/TDs, Rec, Games
elif POSITION_TO_TRAIN == 'TE':
    FEATURES_SEASON_N = ['Age', 'Games', 'GS', 'Targets', 'Receptions', 'Rec Yards', 'Rec TDs']
    TARGET_STATS_SEASON_N_PLUS_1 = ['Rec Yards', 'Rec TDs', 'Receptions', 'Games'] # Predict Rec, Yards, TDs, Games
else:
    raise ValueError(f"Invalid POSITION_TO_TRAIN: {POSITION_TO_TRAIN}")

# --- End Configuration ---

print(f"===== Training Predictive Models for: {POSITION_TO_TRAIN} =====")

# --- Load and Combine Data ---
all_dfs = []
print(f"Loading {POSITION_TO_TRAIN} data for years: {YEARS_TO_LOAD}")
for year in YEARS_TO_LOAD:
    file_pattern = f"{POSITION_TO_TRAIN.lower()}_{year}_stats.csv"
    files = glob.glob(file_pattern)
    if not files:
        print(f"⚠️ Warning: No file found for year {year} matching pattern '{file_pattern}'")
        continue
    try:
        df = pd.read_csv(files[0])
        df['Season'] = year
        all_dfs.append(df)
        print(f"  Loaded {files[0]} ({len(df)} rows)")
    except Exception as e:
        print(f"❌ Error loading {files[0]}: {e}")

if not all_dfs: print("❌ No data loaded. Exiting."); exit()
combined_df = pd.concat(all_dfs, ignore_index=True)
print(f"\nCombined data shape: {combined_df.shape}")

# --- Calculate Fantasy Points (for context/potential future use, not direct target) ---
print("Calculating fantasy points (standard non-PPR)...")
combined_df['Rush Yards'] = pd.to_numeric(combined_df.get('Rush Yards', 0), errors='coerce').fillna(0)
combined_df['Rush TDs'] = pd.to_numeric(combined_df.get('Rush TDs', 0), errors='coerce').fillna(0)
combined_df['Rec Yards'] = pd.to_numeric(combined_df.get('Rec Yards', 0), errors='coerce').fillna(0)
combined_df['Rec TDs'] = pd.to_numeric(combined_df.get('Rec TDs', 0), errors='coerce').fillna(0)
# Add receptions if doing PPR/Half-PPR
# combined_df['Receptions'] = pd.to_numeric(combined_df.get('Receptions', 0), errors='coerce').fillna(0)

combined_df["FantasyPts"] = (
    (combined_df['Rush Yards'] + combined_df['Rec Yards']) * FPTS_YARD +
    (combined_df['Rush TDs'] + combined_df['Rec TDs']) * FPTS_TD
    # + combined_df['Receptions'] * FPTS_RECEPTION # If PPR/Half-PPR
)
print("✅ Calculated Fantasy Points.")

# --- Ensure Target Stat Columns Exist and are Numeric ---
print("Ensuring target stat columns exist and are numeric...")
for col in TARGET_STATS_SEASON_N_PLUS_1:
    if col in combined_df.columns:
        combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce')
    else:
        # Handle common alternatives like G vs Games
        if col == 'Games' and 'G' in combined_df.columns:
             print(f"  Found alternative 'G' for 'Games'. Renaming.")
             combined_df.rename(columns={'G': 'Games'}, inplace=True)
             combined_df['Games'] = pd.to_numeric(combined_df['Games'], errors='coerce')
        else:
            print(f"❌ Error: Target stat column '{col}' not found.")
            exit()

# --- Create Shifted Target Variables (Season N+1 Stats) ---
print("Creating target variables (Stats from next season)...")
combined_df.sort_values(by=['Player', 'Season'], inplace=True)
target_cols_next_season = []
for target_stat in TARGET_STATS_SEASON_N_PLUS_1:
    target_col_next = f"{target_stat}_NextSeason"
    combined_df[target_col_next] = combined_df.groupby('Player')[target_stat].shift(-1)
    target_cols_next_season.append(target_col_next)
print("✅ Created shifted target variables.")

# --- Prepare Feature Data ---
feature_rename_map = {col: f"{col}_N" for col in FEATURES_SEASON_N}
# Check if all features exist before renaming
missing_raw_features = [f for f in FEATURES_SEASON_N if f not in combined_df.columns]
if missing_raw_features:
    # Try to handle G vs Games
    if 'Games' in missing_raw_features and 'G' in combined_df.columns:
        print("  Using 'G' column as 'Games' feature.")
        combined_df.rename(columns={'G': 'Games'}, inplace=True)
        FEATURES_SEASON_N = [f if f != 'Games' else 'Games' for f in FEATURES_SEASON_N] # Ensure list is updated if G was used
        feature_rename_map = {col: f"{col}_N" for col in FEATURES_SEASON_N} # Regenerate map
    else:
        print(f"❌ Error: Raw feature columns missing: {missing_raw_features}")
        exit()

combined_df.rename(columns=feature_rename_map, inplace=True)
features_final = list(feature_rename_map.values())

# Convert feature columns to numeric
for col in features_final:
     if col in combined_df.columns:
         combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce')
     else:
         # This case should be caught earlier, but as a safeguard
         print(f"❌ Error: Feature column '{col}' not found after renaming/checking.")
         exit()

# --- Train Separate Model for Each Target Stat ---
os.makedirs(MODEL_OUTPUT_DIR, exist_ok=True)
print("\n--- Training Individual Models ---")
for i, target_stat in enumerate(TARGET_STATS_SEASON_N_PLUS_1):
    target_col_next = target_cols_next_season[i]
    print(f"\nTraining model for: {target_col_next}")
    current_target_df = combined_df.copy()
    rows_before_target_na = len(current_target_df)
    current_target_df.dropna(subset=[target_col_next], inplace=True)
    print(f"  Removed {rows_before_target_na - len(current_target_df)} rows missing target '{target_col_next}'.")
    rows_before_feature_na = len(current_target_df)
    current_target_df.dropna(subset=features_final, inplace=True)
    print(f"  Removed {rows_before_feature_na - len(current_target_df)} rows missing feature values.")
    if len(current_target_df) < 20:
        print(f"❌ Not enough data pairs for {target_col_next}. Skipping."); continue
    X = current_target_df[features_final]
    y = current_target_df[target_col_next]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"  Training data shape: {X_train.shape}, Testing data shape: {X_test.shape}")
    gbr = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
    gbr.fit(X_train, y_train)
    print("  ✅ Model training complete.")
    y_pred = gbr.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print(f"  📊 Evaluation (MSE): {mse:.2f}, (R^2): {r2:.2f}")
    # Save the individual model with position prefix
    model_filename = os.path.join(MODEL_OUTPUT_DIR, f"{POSITION_TO_TRAIN.lower()}_predictive_{target_stat.lower().replace(' ', '_')}_model.pkl")
    try:
        joblib.dump(gbr, model_filename)
        print(f"  💾 Model saved to {model_filename}")
    except Exception as e:
        print(f"  ❌ Error saving model: {e}")

print(f"\n✅ Finished training all models for {POSITION_TO_TRAIN}.")
