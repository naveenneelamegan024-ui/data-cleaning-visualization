"""
Generates a realistic 'messy' raw retail sales dataset to simulate
the kind of data a data analyst actually receives in the field:
missing values, duplicate rows, inconsistent text casing, and outliers.
"""
import numpy as np
import pandas as pd

np.random.seed(42)

n = 1200
categories = ["Electronics", "Clothing", "Home & Kitchen", "Sports", "Beauty", "Toys"]
regions = ["North", "South", "East", "West"]
payment_methods = ["Credit Card", "Debit Card", "UPI", "Cash on Delivery"]

dates = pd.date_range("2025-01-01", "2025-12-31", freq="D")

df = pd.DataFrame({
    "order_id": [f"ORD{1000+i}" for i in range(n)],
    "order_date": np.random.choice(dates, n),
    "category": np.random.choice(categories, n, p=[0.22, 0.20, 0.18, 0.15, 0.15, 0.10]),
    "region": np.random.choice(regions, n),
    "units_sold": np.random.poisson(4, n) + 1,
    "unit_price": np.round(np.random.gamma(5, 15, n), 2),
    "payment_method": np.random.choice(payment_methods, n),
    "customer_age": np.random.normal(35, 12, n).round().astype(int),
    "customer_rating": np.round(np.random.normal(4.0, 0.8, n), 1),
})

df["revenue"] = (df["units_sold"] * df["unit_price"]).round(2)

# --- inject messiness, like real-world raw data ---

# 1. Missing values in several columns
for col, frac in [("unit_price", 0.05), ("customer_age", 0.07),
                   ("customer_rating", 0.06), ("region", 0.03)]:
    idx = np.random.choice(df.index, int(n * frac), replace=False)
    df.loc[idx, col] = np.nan

# 2. Duplicate rows (simulate double-submitted orders)
dupes = df.sample(25, random_state=1)
df = pd.concat([df, dupes], ignore_index=True)

# 3. Inconsistent text casing / whitespace (common real-world mess)
df["category"] = df["category"].apply(
    lambda x: x.lower() if np.random.rand() < 0.15 else x
)
df["region"] = df["region"].apply(
    lambda x: f" {x} " if pd.notna(x) and np.random.rand() < 0.10 else x
)

# 4. Outliers: a handful of extreme unit prices and ages (data entry errors)
outlier_idx = np.random.choice(df.index, 10, replace=False)
df.loc[outlier_idx[:5], "unit_price"] = df.loc[outlier_idx[:5], "unit_price"] * 20
df.loc[outlier_idx[5:], "customer_age"] = np.random.choice([150, -5, 200], 5)

# 5. Recompute revenue so it stays consistent with the (messy) unit_price
df["revenue"] = (df["units_sold"] * df["unit_price"]).round(2)

df = df.sample(frac=1, random_state=7).reset_index(drop=True)
df.to_csv("/home/claude/project/raw_sales_data.csv", index=False)
print("Raw dataset created:", df.shape)
print(df.isna().sum())
