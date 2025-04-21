import pandas as pd
import joblib

# Load the trained model
model = joblib.load("models/qb_trade_value_model.pkl")

# Load the career stats CSV
df = pd.read_csv("qb_career_stats.csv")

# Ensure correct columns exist
required_columns = ["Yards", "TD", "INT", "Cmp%", "Y/A", "FantasyPts"]
for col in required_columns:
    if col not in df.columns:
        raise ValueError(f"Missing required column: {col}")

# Drop rows with missing values in required columns
df_clean = df.dropna(subset=required_columns)

# Prepare features
X = df_clean[["Yards", "TD", "INT", "Cmp%", "Y/A", "FantasyPts"]]

# Predict trade values
predictions = model.predict(X)

# Add predictions to the DataFrame
df_clean["Predicted Trade Value"] = predictions

# Save to new CSV
df_clean.to_csv("qb_trade_values.csv", index=False)

print("✅ Trade values predicted and saved to qb_trade_values.csv")
