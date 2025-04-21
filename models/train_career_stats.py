import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import glob
import os

# --- Configuration ---
YEARS_TO_LOAD = [2020, 2021, 2022, 2023]
MODEL_OUTPUT_DIR = "models"
MODEL_FILENAME = os.path.join(MODEL_OUTPUT_DIR, "qb_fantasy_predictor_2020_2023.pkl")

# Fantasy Point Calculation Rules
FPTS_PASS_YD = 0.04  # 1 pt per 25 yds
FPTS_PASS_TD = 4
FPTS_INT = -2
FPTS_RUSH_YD = 0.1   # 1 pt per 10 yds
FPTS_RUSH_TD = 6
# --- End Configuration ---

# --- Load Data ---
all_dfs = []
print(f"Loading data for years: {YEARS_TO_LOAD}")
for year in YEARS_TO_LOAD:
    file_pattern = f"qb_{year}_stats.csv"
    files = glob.glob(file_pattern)
    if not files:
        print(f"⚠️ Warning: No file found for year {year} matching pattern '{file_pattern}'")
        continue
    try:
        df = pd.read_csv(files[0])
        df['Season'] = year # Add season year for reference
        all_dfs.append(df)
        print(f"  Loaded {files[0]} ({len(df)} rows)")
    except Exception as e:
        print(f"❌ Error loading {files[0]}: {e}")

if not all_dfs:
    print("❌ No data loaded. Exiting.")
    exit()

combined_df = pd.concat(all_dfs, ignore_index=True)
print(f"Combined data shape: {combined_df.shape}")

# --- Calculate Fantasy Points ---
# Ensure necessary columns are numeric, fill NaNs with 0 before calculation
stat_cols = ['Pass Yards', 'Pass TDs', 'Interceptions', 'Rush Yards', 'Rush TDs']
for col in stat_cols:
    if col in combined_df.columns:
        combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce').fillna(0)
    else:
        print(f"⚠️ Warning: Column '{col}' not found for fantasy point calculation. Treating as 0.")
        combined_df[col] = 0 # Add column if missing and set to 0

combined_df["FantasyPts"] = (
    combined_df["Pass Yards"] * FPTS_PASS_YD +
    combined_df["Pass TDs"] * FPTS_PASS_TD +
    combined_df["Interceptions"] * FPTS_INT +
    combined_df["Rush Yards"] * FPTS_RUSH_YD +
    combined_df["Rush TDs"] * FPTS_RUSH_TD
)
print("✅ Calculated Fantasy Points.")

# --- Define Features and Target ---
# Select features relevant for predicting fantasy points
features = [
    'Age',
    'Games',
    # 'Games Started', # Often highly correlated with Games
    'Completions',
    'Pass Atts',
    'Pass Yards',
    'Pass TDs',
    'Interceptions',
    'Passer Rating',
    'Rush Atts',
    'Rush Yards',
    'Rush TDs'
]
target = "FantasyPts"

# Ensure all selected feature columns exist, fill missing numeric features with 0 or median?
# For simplicity, let's ensure they exist and rely on dropna later.
missing_features = [f for f in features if f not in combined_df.columns]
if missing_features:
    print(f"❌ Error: The following required feature columns are missing: {missing_features}")
    exit()

# Convert feature columns to numeric, coercing errors
for col in features:
     combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce')

# --- Clean Data ---
cols_to_check = features + [target]
initial_rows = len(combined_df)
combined_df.dropna(subset=cols_to_check, inplace=True)
final_rows = len(combined_df)
print(f"Removed {initial_rows - final_rows} rows with missing values in features or target.")

# --- Train Model ---
if final_rows < 10: # Increased threshold slightly
    print(f"❌ Not enough data to train the model after cleaning. Only {final_rows} rows remain.")
else:
    X = combined_df[features]
    y = combined_df[target]

    # Train-test split (evaluating on a portion of 2020-2023 data)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"Training data shape: {X_train.shape}")
    print(f"Testing data shape: {X_test.shape}")

    # Train model
    model = LinearRegression()
    model.fit(X_train, y_train)
    print("✅ Model training complete.")

    # Predict and evaluate on the test set (from 2020-2023 data)
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print("\n--- Model Evaluation (on 20% held-out 2020-2023 data) ---")
    print(f"📉 Mean Squared Error (MSE): {mse:.2f}")
    print(f"📈 R^2 Score: {r2:.2f}")

    # --- Save Model ---
    try:
        # Create output directory if it doesn't exist
        os.makedirs(MODEL_OUTPUT_DIR, exist_ok=True)
        joblib.dump(model, MODEL_FILENAME)
        print(f"💾 Model saved to {MODEL_FILENAME}")
    except Exception as e:
        print(f"❌ Error saving model: {e}")

    print("✅ Model training and evaluation process finished.")

