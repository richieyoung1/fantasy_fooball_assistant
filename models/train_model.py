import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import make_pipeline
from sklearn.compose import ColumnTransformer
import joblib
import os

# Load the data
df = pd.read_csv("players.csv")
df = df.dropna(subset=["PPG", "Proj ROS", "Rank", "Pos"])

# Features and label
X = df[["PPG", "Proj ROS", "Rank", "Pos"]]
# Estimated trade value formula (you can adjust this later)
y = df["PPG"] * 4 + df["Proj ROS"] * 0.2 - df["Rank"]

# Preprocessing pipeline
preprocessor = ColumnTransformer(
    transformers=[("pos", OneHotEncoder(handle_unknown="ignore"), ["Pos"])],
    remainder="passthrough"
)

# Build model pipeline
model = make_pipeline(preprocessor, RandomForestRegressor(n_estimators=100, random_state=42))

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model.fit(X_train, y_train)

# Evaluate
score = model.score(X_test, y_test)
print(f"✅ Model trained! R^2 score: {score:.2f}")

# Save model
os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/trade_value_model.pkl")
print("📦 Model saved to models/trade_value_model.pkl")
