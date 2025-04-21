import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import joblib

# Load the dataset
df = pd.read_csv("qb_2023_stats.csv")

# Drop rows with missing data in required columns
df = df.dropna(subset=["Yards", "Touchdowns", "Interceptions", "Rush Yards", "Rush TDs", "Passer Rating"])

# Select features and target
features = ["Yards", "Touchdowns", "Interceptions", "Rush Yards", "Rush TDs"]
X = df[features]
y = df["Passer Rating"]

# Train the model
model = LinearRegression()
model.fit(X, y)

# Evaluate the model
predictions = model.predict(X)
mse = mean_squared_error(y, predictions)
r2 = r2_score(y, predictions)

print("✅ Model trained with passing + rushing stats!")
print(f"📉 MSE: {mse:.2f}")
print(f"📈 R^2 Score: {r2:.2f}")

# Save the model
joblib.dump(model, "models/qb_passer_rating_model.pkl")
print("💾 Model saved to models/qb_passer_rating_model.pkl")
