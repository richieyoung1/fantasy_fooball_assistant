import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Load your QB data
df = pd.read_csv("qb_2023_stats.csv")

# Drop rows with missing values
df = df.dropna(subset=["Rush Attempts", "Rush Yards", "Rush TDs"])

# Select features for clustering
X = df[["Rush Attempts", "Rush Yards", "Rush TDs"]]

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Perform KMeans clustering
kmeans = KMeans(n_clusters=3, random_state=42)
clusters = kmeans.fit_predict(X_scaled)

# Assign labels based on cluster rank (by total Rush Yards)
centers = pd.DataFrame(kmeans.cluster_centers_, columns=X.columns)
centers["Total"] = centers["Rush Yards"]  # Just use Rush Yards to rank
ranked_clusters = centers.sort_values("Total").index.tolist()

style_map = {
    ranked_clusters[0]: "Pocket Passer",
    ranked_clusters[1]: "Balanced",
    ranked_clusters[2]: "Scrambler"
}
df["QB Style"] = [style_map[c] for c in clusters]

# Save updated file
df.to_csv("qb_2023_stats.csv", index=False)
print("✅ Clustered QB styles added and saved to qb_2023_stats.csv")
