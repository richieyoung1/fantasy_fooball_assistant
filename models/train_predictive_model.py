import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import glob
import os
import numpy as np

# --- Configuration ---
TRAINING_YEARS = [2020, 2021, 2022, 2023, 2024]
MODEL_OUTPUT_DIR = "models"

# Fantasy Point Calculation Rules (used later for context, not direct target)
FPTS_PASS_YD = 0.04
FPTS_PASS_TD = 4
FPTS_INT = -2
FPTS_RUSH_YD = 0.1
FPTS_RUSH_TD = 6

# Features from Season N to use for predicting Season N+1 stats
FEATURES_SEASON_N = [
    'Age', 'Games', 'Completions', 'Pass Atts', 'Pass Yards', 'Pass TDs',
    'Interceptions', 'Passer Rating', 'Rush Atts', 'Rush Yards', 'Rush TDs'
]

# Target stats from Season N+1 we want to predict individually
TARGET_STATS_SEASON_N_PLUS_1 = [
    'Pass Yards', 'Pass TDs', 'Interceptions', 'Rush Yards', 'Rush TDs',
    'Games' # <-- Added Games here
]
# --- End Configuration ---

# --- Load and Combine Data ---
all_dfs = []
print(f"Loading data for years: {TRAINING_YEARS}")
for year in TRAINING_YEARS:
    file_pattern = f"qb_{year}_stats.csv"
    files = glob.glob(file_pattern)
    if not files:
        print(f"⚠️ Warning: No file found for year {year} matching pattern '{file_pattern}'")
        continue
    try:
        df = pd.read_csv(files[0])
        df['Season'] = year # Add season year
        all_dfs.append(df)
        print(f"  Loaded {files[0]} ({len(df)} rows)")
    except Exception as e:
        print(f"❌ Error loading {files[0]}: {e}")

if not all_dfs:
    print("❌ No data loaded. Exiting.")
    exit()

combined_df = pd.concat(all_dfs, ignore_index=True)
print(f"\nCombined data shape: {combined_df.shape}")

# --- Ensure Target Stat Columns Exist and are Numeric ---
print("Ensuring target stat columns exist and are numeric...")
for col in TARGET_STATS_SEASON_N_PLUS_1:
    if col in combined_df.columns:
        combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce') # Keep NaNs for now
    else:
        print(f"❌ Error: Target stat column '{col}' not found in the loaded data.")
        # Attempt to find alternative (e.g. 'G' for 'Games') - simplistic example
        if col == 'Games' and 'G' in combined_df.columns:
             print(f"  Found alternative 'G' for 'Games'. Renaming.")
             combined_df.rename(columns={'G': 'Games'}, inplace=True)
             combined_df['Games'] = pd.to_numeric(combined_df['Games'], errors='coerce')
        else:
            print(f"  No alternative found for '{col}'. Exiting.")
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
# Rename feature columns to indicate they are from Season N
feature_rename_map = {col: f"{col}_N" for col in FEATURES_SEASON_N}
combined_df.rename(columns=feature_rename_map, inplace=True)
features_final = list(feature_rename_map.values())

# Convert feature columns to numeric
for col in features_final:
     # Check if column exists before conversion
     if col in combined_df.columns:
         combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce')
     else:
         # Handle case where a feature might be missing after rename (e.g., if 'G' was used for 'Games')
         raw_feature = col.replace('_N', '')
         if raw_feature in combined_df.columns:
              print(f"  Renaming '{raw_feature}' to '{col}' for feature set.")
              combined_df.rename(columns={raw_feature: col}, inplace=True)
              combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce')
         else:
              print(f"❌ Error: Feature column '{col}' (or its raw form '{raw_feature}') not found after renaming.")
              exit()


# --- Train Separate Model for Each Target Stat ---
os.makedirs(MODEL_OUTPUT_DIR, exist_ok=True) # Ensure model directory exists

print("\n--- Training Individual Models for Each Target Stat ---")
for i, target_stat in enumerate(TARGET_STATS_SEASON_N_PLUS_1):
    target_col_next = target_cols_next_season[i]
    print(f"\nTraining model for: {target_col_next}")

    # Prepare data specific to this target
    current_target_df = combined_df.copy() # Work on a copy

    # Drop rows where this specific target is missing
    rows_before_target_na = len(current_target_df)
    current_target_df.dropna(subset=[target_col_next], inplace=True)
    print(f"  Removed {rows_before_target_na - len(current_target_df)} rows missing target '{target_col_next}'.")

    # Drop rows where any features are missing
    rows_before_feature_na = len(current_target_df)
    current_target_df.dropna(subset=features_final, inplace=True)
    print(f"  Removed {rows_before_feature_na - len(current_target_df)} rows missing feature values.")

    if len(current_target_df) < 20:
        print(f"❌ Not enough data pairs to train model for {target_col_next}. Only {len(current_target_df)} rows remain. Skipping.")
        continue

    X = current_target_df[features_final]
    y = current_target_df[target_col_next]

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"  Training data shape: {X_train.shape}")
    print(f"  Testing data shape: {X_test.shape}")

    # Initialize and Train Gradient Boosting Model
    gbr = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
    gbr.fit(X_train, y_train)
    print("  ✅ Model training complete.")

    # Evaluate on the test set
    y_pred = gbr.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print(f"  📊 Evaluation (MSE): {mse:.2f}, (R^2): {r2:.2f}")

    # Save the individual model
    model_filename = os.path.join(MODEL_OUTPUT_DIR, f"qb_predictive_{target_stat.lower().replace(' ', '_')}_model.pkl")
    try:
        joblib.dump(gbr, model_filename)
        print(f"  💾 Model saved to {model_filename}")
    except Exception as e:
        print(f"  ❌ Error saving model: {e}")

print("\n✅ Finished training all individual predictive models.")
