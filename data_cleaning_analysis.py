"""
Data Cleaning & Visualization Project
--------------------------------------
Dataset: Retail sales data (raw_sales_data.csv)
Goal: Clean a messy raw dataset (missing values, duplicates, outliers,
inconsistent formatting) and visualize key business insights.

Author: [Your Name]
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

sns.set_theme(style="whitegrid", palette="deep")
OUT = "/home/claude/project/plots"
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------
# 1. LOAD & INITIAL EXPLORATION
# ---------------------------------------------------------
df = pd.read_csv("/home/claude/project/raw_sales_data.csv", parse_dates=["order_date"])

print("=" * 60)
print("INITIAL SHAPE:", df.shape)
print("=" * 60)
print(df.info())
print("\nMissing values per column:\n", df.isna().sum())
print("\nDuplicate rows:", df.duplicated().sum())

# Missing-value heatmap BEFORE cleaning
plt.figure(figsize=(9, 5))
sns.heatmap(df.isna(), cbar=False, cmap="rocket_r")
plt.title("Missing Values Before Cleaning")
plt.tight_layout()
plt.savefig(f"{OUT}/01_missing_values_before.png", dpi=150)
plt.close()

# ---------------------------------------------------------
# 2. CLEAN: DUPLICATES
# ---------------------------------------------------------
before = len(df)
df = df.drop_duplicates(subset=["order_id"]).copy()
print(f"\nRemoved {before - len(df)} duplicate rows based on order_id")

# ---------------------------------------------------------
# 3. CLEAN: TEXT / FORMATTING INCONSISTENCIES
# ---------------------------------------------------------
df["category"] = df["category"].str.strip().str.title()
df["region"] = df["region"].str.strip().str.title()

# ---------------------------------------------------------
# 4. CLEAN: MISSING VALUES
# ---------------------------------------------------------
# region: categorical -> fill with mode
df["region"] = df["region"].fillna(df["region"].mode()[0])

# unit_price: numeric, skewed -> fill with median per category (more accurate
# than a single global median since prices differ a lot by category)
df["unit_price"] = df.groupby("category")["unit_price"].transform(
    lambda x: x.fillna(x.median())
)

# customer_age: fill with overall median (robust to outliers vs mean)
df["customer_age"] = df["customer_age"].fillna(df["customer_age"].median())

# customer_rating: fill with median
df["customer_rating"] = df["customer_rating"].fillna(df["customer_rating"].median())

# recompute revenue after price imputation, so it stays internally consistent
df["revenue"] = (df["units_sold"] * df["unit_price"]).round(2)

print("\nMissing values after imputation:\n", df.isna().sum())

# ---------------------------------------------------------
# 5. CLEAN: OUTLIERS (IQR method)
# ---------------------------------------------------------
def iqr_bounds(series, k=1.5):
    q1, q3 = series.quantile([0.25, 0.75])
    iqr = q3 - q1
    return q1 - k * iqr, q3 + k * iqr

# unit_price outliers
low, high = iqr_bounds(df["unit_price"])
price_outliers = df[(df["unit_price"] < low) | (df["unit_price"] > high)]
print(f"\nunit_price outliers detected (IQR method): {len(price_outliers)}")
df["unit_price"] = df["unit_price"].clip(lower=max(low, 0), upper=high)

# customer_age: business rule (valid human ages) + IQR sanity check
invalid_age = df[(df["customer_age"] < 10) | (df["customer_age"] > 90)]
print(f"customer_age business-rule violations: {len(invalid_age)}")
df["customer_age"] = df["customer_age"].clip(lower=15, upper=85)

# recompute revenue post-clipping
df["revenue"] = (df["units_sold"] * df["unit_price"]).round(2)

# Boxplots before/after outlier treatment (recreate 'before' from raw copy)
raw = pd.read_csv("/home/claude/project/raw_sales_data.csv")
fig, axes = plt.subplots(1, 2, figsize=(11, 5))
sns.boxplot(y=raw["unit_price"].dropna(), ax=axes[0], color="salmon")
axes[0].set_title("Unit Price — Before Cleaning")
sns.boxplot(y=df["unit_price"], ax=axes[1], color="mediumseagreen")
axes[1].set_title("Unit Price — After Outlier Treatment")
plt.tight_layout()
plt.savefig(f"{OUT}/02_outlier_treatment_price.png", dpi=150)
plt.close()

# ---------------------------------------------------------
# 6. SAVE CLEANED DATASET
# ---------------------------------------------------------
df.to_csv("/home/claude/project/cleaned_sales_data.csv", index=False)
print(f"\nFinal cleaned shape: {df.shape}")
print("Saved -> cleaned_sales_data.csv")

# ===========================================================
# 7. VISUAL STORYTELLING — KEY BUSINESS INSIGHTS
# ===========================================================

# (a) Revenue by category
plt.figure(figsize=(8, 5))
rev_by_cat = df.groupby("category")["revenue"].sum().sort_values(ascending=False)
sns.barplot(x=rev_by_cat.values, y=rev_by_cat.index, palette="viridis")
plt.title("Total Revenue by Category")
plt.xlabel("Revenue (₹)")
plt.tight_layout()
plt.savefig(f"{OUT}/03_revenue_by_category.png", dpi=150)
plt.close()

# (b) Monthly revenue trend
df["month"] = df["order_date"].dt.to_period("M").astype(str)
monthly = df.groupby("month")["revenue"].sum()
plt.figure(figsize=(10, 5))
monthly.plot(marker="o", color="steelblue")
plt.title("Monthly Revenue Trend (2025)")
plt.ylabel("Revenue (₹)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{OUT}/04_monthly_revenue_trend.png", dpi=150)
plt.close()

# (c) Revenue by region and payment method (stacked)
pivot = df.pivot_table(index="region", columns="payment_method",
                        values="revenue", aggfunc="sum", fill_value=0)
pivot.plot(kind="bar", stacked=True, figsize=(9, 5), colormap="Set2")
plt.title("Revenue by Region, Split by Payment Method")
plt.ylabel("Revenue (₹)")
plt.tight_layout()
plt.savefig(f"{OUT}/05_region_payment_revenue.png", dpi=150)
plt.close()

# (d) Correlation heatmap
plt.figure(figsize=(7, 5))
num_cols = ["units_sold", "unit_price", "customer_age", "customer_rating", "revenue"]
sns.heatmap(df[num_cols].corr(), annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Correlation Between Numeric Features")
plt.tight_layout()
plt.savefig(f"{OUT}/06_correlation_heatmap.png", dpi=150)
plt.close()

# (e) Customer age distribution vs rating
plt.figure(figsize=(8, 5))
sns.scatterplot(data=df, x="customer_age", y="customer_rating",
                 hue="category", alpha=0.6)
plt.title("Customer Age vs Rating by Category")
plt.tight_layout()
plt.savefig(f"{OUT}/07_age_vs_rating.png", dpi=150)
plt.close()

print("\nAll plots saved to:", OUT)
print("\nDONE.")
