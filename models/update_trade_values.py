import pandas as pd
import joblib

# Load model
model = joblib.load("models/trade_value_model.pkl")

# Load player data
df = pd.read_csv("players.csv")

# Drop rows with missing required values
df = df.dropna(subset=["PPG", "Proj ROS", "Rank", "Pos"])

# Predict trade values
X = df[["PPG", "Proj ROS", "Rank", "Pos"]]
predictions = model.predict(X)

# Add predictions to DataFrame
df["Trade Value"] = predictions.round(2)

# Save updated CSV
df.to_csv("players.csv", index=False)
print("✅ Trade values added and saved to players.csv")
