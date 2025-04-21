import pandas as pd
import joblib
from sklearn.metrics import mean_squared_error, r2_score
import os

# --- Configuration ---
MODEL_PATH = os.path.join("models", "qb_fantasy_predictor_2020_2023.pkl")
DATA_YEAR = 2024
DATA_PATH = f"qb_{DATA_YEAR}_stats.csv"

# Must match the features used during training
FEATURES = [
    'Age', 'Games', 'Completions', 'Pass Atts', 'Pass Yards', 'Pass TDs',
    'Interceptions', 'Passer Rating', 'Rush Atts', 'Rush Yards', 'Rush TDs'
]
TARGET = "FantasyPts" # Actual fantasy points column name

# Fantasy Point Calculation Rules (must match training script)
FPTS_PASS_YD = 0.04
FPTS_PASS_TD = 4
FPTS_INT = -2
FPTS_RUSH_YD = 0.1
FPTS_RUSH_TD = 6
# --- End Configuration ---

# --- Load Model ---
print(f"Loading model from {MODEL_PATH}...")
if not os.path.exists(MODEL_PATH):
    print(f"❌ Error: Model file not found at {MODEL_PATH}")
    print("Please ensure you have run the training script first.")
    exit()
try:
    model = joblib.load(MODEL_PATH)
    print("✅ Model loaded successfully.")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    exit()

# --- Load 2024 Data ---
print(f"Loading data for {DATA_YEAR} from {DATA_PATH}...")
if not os.path.exists(DATA_PATH):
    print(f"❌ Error: Data file not found at {DATA_PATH}")
    print(f"Please ensure you have run the scraping script for the year {DATA_YEAR}.")
    exit()
try:
    df_2024 = pd.read_csv(DATA_PATH)
    print(f"✅ Loaded {DATA_PATH} ({len(df_2024)} rows)")
except Exception as e:
    print(f"❌ Error loading data: {e}")
    exit()

# --- Prepare 2024 Data ---
print("Preparing 2024 data for prediction...")

# 1. Calculate Actual Fantasy Points for 2024
stat_cols = ['Pass Yards', 'Pass TDs', 'Interceptions', 'Rush Yards', 'Rush TDs']
for col in stat_cols:
    if col in df_2024.columns:
        df_2024[col] = pd.to_numeric(df_2024[col], errors='coerce').fillna(0)
    else:
        print(f"⚠️ Warning: Column '{col}' not found in {DATA_YEAR} data for fantasy point calculation. Treating as 0.")
        df_2024[col] = 0

df_2024[TARGET] = (
    df_2024["Pass Yards"] * FPTS_PASS_YD +
    df_2024["Pass TDs"] * FPTS_PASS_TD +
    df_2024["Interceptions"] * FPTS_INT +
    df_2024["Rush Yards"] * FPTS_RUSH_YD +
    df_2024["Rush TDs"] * FPTS_RUSH_TD
)
print("  Calculated actual fantasy points for 2024.")

# 2. Ensure all feature columns exist
missing_features = [f for f in FEATURES if f not in df_2024.columns]
if missing_features:
    print(f"❌ Error: The following required feature columns are missing from {DATA_PATH}: {missing_features}")
    # Attempt to fill missing features with 0 if appropriate, otherwise exit
    can_fill = True
    for mf in missing_features:
        # Example: Only fill if it's a stat column, not something like 'Age' if missing
        if mf not in ['Completions', 'Pass Atts', 'Pass Yards', 'Pass TDs', 'Interceptions', 'Passer Rating', 'Rush Atts', 'Rush Yards', 'Rush TDs', 'Games']:
             can_fill = False
             break
    if can_fill:
         print(f"  Attempting to fill missing features {missing_features} with 0...")
         for mf in missing_features:
             df_2024[mf] = 0
    else:
        print("  Cannot reliably fill missing features. Exiting.")
        exit()


# 3. Convert feature columns to numeric
for col in FEATURES:
     df_2024[col] = pd.to_numeric(df_2024[col], errors='coerce')

# 4. Handle missing values (NaN) in features - IMPORTANT: Use same strategy as training
# The training script used dropna. We should do the same here for consistency.
initial_rows = len(df_2024)
df_2024.dropna(subset=FEATURES + [TARGET], inplace=True) # Also drop if actual fantasy points calculation failed
final_rows = len(df_2024)
print(f"  Removed {initial_rows - final_rows} rows with missing values in features or target.")

if final_rows == 0:
    print(f"❌ No valid data remaining for {DATA_YEAR} after cleaning. Cannot make predictions.")
    exit()

# 5. Select features (X) and actual target (y)
X_2024 = df_2024[FEATURES]
y_2024_actual = df_2024[TARGET]
print("✅ Data preparation complete.")

# --- Make Predictions ---
print("Making predictions on 2024 data...")
try:
    y_2024_pred = model.predict(X_2024)
    df_2024['PredictedFantasyPts'] = y_2024_pred
    print("✅ Predictions generated.")
except Exception as e:
    print(f"❌ Error during prediction: {e}")
    exit()

# --- Evaluate Predictions ---
print(f"\n--- Evaluating Model Performance on {DATA_YEAR} Data ---")
mse = mean_squared_error(y_2024_actual, y_2024_pred)
r2 = r2_score(y_2024_actual, y_2024_pred)

print(f"📉 Mean Squared Error (MSE): {mse:.2f}")
print(f"📈 R^2 Score: {r2:.2f}")
print("----------------------------------------------------")

# --- Display Results ---
# Show top N players based on actual fantasy points for comparison
N = 20
df_display = df_2024[['Player', TARGET, 'PredictedFantasyPts']].copy()
df_display['PredictionError'] = df_display[TARGET] - df_display['PredictedFantasyPts']
df_display = df_display.sort_values(by=TARGET, ascending=False)

print(f"\n--- Top {N} Players ({DATA_YEAR}) - Actual vs. Predicted Fantasy Points ---")
print(df_display.head(N).to_string(index=False, float_format="%.2f"))
print("----------------------------------------------------")

print("\n✅ Prediction and evaluation finished.")

# --- Save Predictions ---
print(f"\nSaving predictions to {DATA_PATH}...")
df_2024.to_csv(DATA_PATH, index=False)
print("✅ Predictions saved to CSV file.")