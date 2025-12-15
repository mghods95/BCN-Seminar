# Example main code script

import numpy as np
import argparse
import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Display full DataFrame output without truncation
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

print("\n\n")

# =====================================================
# 1. Load the raw dataset
# =====================================================
df = pd.read_csv("bcn.csv")


print("\n\n")
print(df.head())            # Show first rows
print("\n\n")
print(df.isna().sum())      # Count missing values per column
print("\n\n")
print(df.info())            # Show column types and memory usage


# =====================================================
# 2. Remove unnecessary identifier columns
#    (these columns do not help with modeling or analysis)
# =====================================================
cols_to_remove = {
    "Transaction ID",
    "Item ID",
    "Supplier ID",
    "Customer ID",
    "GPS Coordinates",
    "Transaction Hash"
}

# Only drop columns that actually exist in the dataset
existing_cols = list(set(df.columns) & cols_to_remove)

df.drop(existing_cols, axis=1, inplace=True)

print("\n\n")
print(df.head())   # Show updated dataset after dropping columns


# =====================================================
# (You printed df.head() again here — kept as requested)
# =====================================================
print("\n\n")
print(df.head())


# =====================================================
# 3. Feature engineering from Timestamp column
#    Create weekday, month, year — useful for time-based patterns
# =====================================================

# Reload dataset (your original code did this again — I keep it exactly the same)
df = pd.read_csv("bcn.csv")


# Convert Timestamp → datetime format
df['OrderDateTime'] = pd.to_datetime(df['Timestamp'])

# Add time-based features
df['Weekday_Num'] = df['OrderDateTime'].dt.weekday   # Monday=0 ... Sunday=6
df['Month_Num']   = df['OrderDateTime'].dt.month
df['Year_Num']    = df['OrderDateTime'].dt.year

# Calculate time gap between consecutive transactions
df['TimeGap_Seconds'] = df['OrderDateTime'].diff().dt.total_seconds()

# Remove original timestamp and helper column
df.drop(columns=['Timestamp', 'TimeGap_Seconds'], inplace=True)

print("\n\n")
print(df.head())     # Show dataframe with new features


# =====================================================
# 4. One-hot encode categorical variables
# =====================================================

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Reload dataset again (kept exactly as your original code)
df = pd.read_csv("bcn.csv")


# Columns that should be converted into dummy variables
categorical_cols = ["Smart Contract Status", "Order Status", "Payment Status"]

# Only include columns that actually exist in the dataset
existing_categorical_cols = [col for col in categorical_cols if col in df.columns]

# Encode categorical variables → one-hot dummy variables
df = pd.get_dummies(df, columns=existing_categorical_cols, drop_first=False)
print("\n\n")
print(df.head())     # Check encoding result


# =====================================================
# 5. Groupby analysis: overall averages by Location
# =====================================================
gp = df.groupby("Location")[["Order Amount", "Quantity Shipped",
                             "Quantity Mismatch"]].mean()

print("\n\n")
print(gp)


# =====================================================
# 6. Fraud analysis: Compare metrics for Fraud Indicator = 1
# =====================================================
print("\n\n")
print(
    df[df["Fraud Indicator"] == 1]
    .groupby("Location")[["Order Amount", "Quantity Mismatch"]]
    .mean()
)


# =====================================================
# 7. Fun console messages
#    (kept exactly as your code)
# =====================================================
print("\n\nThis is an Example of a Quantlet")
print("\n\nBatman")








# ============================================================
# Quantlet: BlockchainAcrossIndustries
# Title: Blockchain Transaction Analytics Across Industries
# Description:
#   Loads the bcn.csv dataset, cleans features, engineers
#   time-based attributes, performs descriptive analytics,
#   analyzes fraud behavior, and generates visualizations.
# ============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

plt.savefig("order_amount_distribution.png", dpi=300, bbox_inches="tight")


# Display settings
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

print("\n=== 1. Load Dataset ===\n")
df = pd.read_csv("bcn.csv")

print(df.head())
print("\nMissing values:\n", df.isna().sum())


# =====================================================
# 2. Remove identifier columns (not useful for analysis)
# =====================================================
print("\n=== 2. Cleaning Identifier Columns ===\n")

cols_to_remove = {
    "Transaction ID",
    "Item ID",
    "Supplier ID",
    "Customer ID",
    "GPS Coordinates",
    "Transaction Hash"
}

existing_cols = list(set(df.columns) & cols_to_remove)
df.drop(existing_cols, axis=1, inplace=True)

print("Removed columns:", existing_cols)
print(df.head())


# =====================================================
# 3. Feature Engineering from Timestamps
# =====================================================
print("\n=== 3. Feature Engineering ===\n")

df["OrderDateTime"] = pd.to_datetime(df["Timestamp"])
df["Weekday_Num"] = df["OrderDateTime"].dt.weekday
df["Month_Num"] = df["OrderDateTime"].dt.month
df["Year_Num"] = df["OrderDateTime"].dt.year

# Sort to compute time gaps
df = df.sort_values("OrderDateTime")
df["TimeGap_Seconds"] = df["OrderDateTime"].diff().dt.total_seconds()

df.drop(columns=["Timestamp"], inplace=True)

print(df[["OrderDateTime", "Weekday_Num", "Month_Num", "Year_Num"]].head())


# =====================================================
# 4. One-hot Encode Categorical Variables
# =====================================================
print("\n=== 4. One-Hot Encoding ===\n")

categorical_cols = ["Smart Contract Status", "Order Status", "Payment Status"]
existing_categorical_cols = [c for c in categorical_cols if c in df.columns]

df = pd.get_dummies(df, columns=existing_categorical_cols, drop_first=False)

print("Encoded categorical variables:", existing_categorical_cols)
print(df.head())







# =====================================================
# 5.5 Feature Importance (RandomForest)
# =====================================================
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

target_col = "Fraud Indicator"
if target_col not in df.columns:
    raise ValueError(f"Missing target column: {target_col}")

# X / y
X = df.drop(columns=[target_col], errors="ignore")
y = df[target_col]

# --- FIX: drop datetime columns (RandomForest can't handle datetime64 directly) ---
datetime_cols = X.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]"]).columns
X = X.drop(columns=list(datetime_cols), errors="ignore")

# One-hot encode any remaining categorical columns (e.g., Location)
X = pd.get_dummies(X, drop_first=False)

# Optional but clean: convert bool columns to int
bool_cols = X.select_dtypes(include=["bool"]).columns
X[bool_cols] = X[bool_cols].astype(int)

# Clean NaNs / infs
X = X.replace([np.inf, -np.inf], np.nan).fillna(0)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y if y.nunique() > 1 else None
)

# Train model
rf = RandomForestClassifier(n_estimators=400, random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)

# Build importance_df
importance_df = pd.DataFrame({
    "Feature": X.columns,
    "Importance": rf.feature_importances_
}).sort_values("Importance", ascending=True)

# Save full table
importance_df.to_csv("feature_importance_all.csv", index=False)

# Plot top N (like your screenshot)
top_n = 25
plot_df = importance_df.tail(top_n)

plt.figure(figsize=(14, 7))
plt.barh(plot_df["Feature"], plot_df["Importance"])
plt.title("Feature Importance")
plt.xlabel("Importance")
plt.tight_layout()
plt.savefig("feature_importance_top25.png", dpi=300, bbox_inches="tight")
plt.close()













# =====================================================
# 5. Groupby Analysis by Location
# =====================================================
print("\n=== 5. Descriptive Analysis by Location ===\n")

gp = df.groupby("Location")[["Order Amount", "Quantity Shipped",
                             "Quantity Mismatch"]].mean()
print(gp)


# =====================================================
# 6. Fraud Analysis (Fraud Indicator = 1)
# =====================================================
print("\n=== 6. Fraud Analysis ===\n")

fraud_stats = (
    df[df["Fraud Indicator"] == 1]
    .groupby("Location")[["Order Amount", "Quantity Mismatch"]]
    .mean()
)

print(fraud_stats)


# =====================================================
# 7. Visualization: Order Amount Distribution
# =====================================================
print("\n=== 7. Plot: Distribution of Order Amount ===\n")

plt.figure(figsize=(10, 6))
sns.histplot(df["Order Amount"], bins=40)
plt.title("Distribution of Order Amounts")
plt.xlabel("Order Amount")
plt.ylabel("Count")

plt.tight_layout()
plt.savefig("order_amount_distribution.png", dpi=300, bbox_inches="tight")
plt.close()






# =====================================================
# 8. Visualization: Fraud vs Non-Fraud Comparison
# =====================================================
print("\n=== 8. Plot: Fraud vs Non-Fraud Order Amount ===\n")

plt.figure(figsize=(10, 6))
sns.boxplot(
    data=df,
    x="Fraud Indicator",
    y="Order Amount"
)
plt.title("Fraud vs Non-Fraud Order Amount")
plt.xlabel("Fraud Indicator (0 = Normal, 1 = Fraud)")
plt.ylabel("Order Amount")

plt.tight_layout()
plt.savefig("fraud_vs_nonfraud_order_amount.png", dpi=300, bbox_inches="tight")
plt.close()








# =====================================================
# 9. Final Summary
# =====================================================
print("\n=== 9. Summary of Key Insights ===\n")
print("* Dataset cleaned and processed.")
print("* Time-based features (weekday, month, year) were created.")
print("* One-hot encoding applied to categorical fields.")
print("* Location-level averages were computed.")
print("* Fraud transactions analyzed separately.")
print("* Two plots saved to /output/:")
print("  - order_amount_distribution.png")
print("  - fraud_vs_nonfraud_order_amount.png")

print("\nQuantlet script completed successfully.\n")


