# Data Cleaning & Visualization Project — Retail Sales Analysis

## 1. Objective
Clean a raw, messy retail sales dataset and extract visual insights on revenue drivers, so the results can support business decisions (inventory, marketing spend, regional strategy).

## 2. Dataset
`raw_sales_data.csv` — 1,225 synthetic e-commerce order records for 2025, covering category, region, pricing, payment method, and customer demographics. The data intentionally mirrors real-world messiness: missing values, duplicate orders, inconsistent text formatting, and data-entry outliers.

## 3. Data Quality Issues Found

| Issue | Details |
|---|---|
| Missing values | `region` (37), `unit_price` (60), `customer_age` (85), `customer_rating` (72) |
| Duplicate rows | 25 duplicate `order_id`s (simulating double-submitted orders) |
| Inconsistent formatting | Mixed casing in `category`/`region` (e.g. "electronics" vs "Electronics"), stray whitespace |
| Outliers | 30 unit-price outliers (IQR method) from data-entry errors; 17 invalid `customer_age` values (e.g. 200, -5) |

## 4. Cleaning Approach
- **Duplicates:** dropped by `order_id`.
- **Text formatting:** standardized casing and stripped whitespace.
- **Missing values:** `region` filled with mode; `unit_price` filled with **category-level median** (more accurate than a global median since prices vary a lot by category); `customer_age` and `customer_rating` filled with overall median (robust to skew).
- **Outliers:** detected with the IQR method (1.5× IQR) and treated with clipping (winsorization) rather than deletion, to preserve sample size while capping unrealistic values. `customer_age` also constrained to a valid business range (15–85).
- `revenue` was recomputed after cleaning so it stays internally consistent with cleaned `unit_price`.

Final cleaned dataset: **1,200 rows × 10 columns**, zero missing values.

## 5. Key Insights
- **Electronics** is the top revenue-generating category, followed by Clothing and Home & Kitchen; Toys generates the least.
- Monthly revenue shows [see chart] seasonal fluctuation across 2025 rather than a flat trend.
- **North/South regions** carry more revenue via Credit Card and UPI than Cash on Delivery.
- Correlation analysis shows `revenue` is driven primarily by `unit_price` and `units_sold`, with **no meaningful correlation** between customer age/rating and spend — suggesting marketing shouldn't over-index on age-based targeting.

## 6. Visualizations
All charts are in `/plots`:
1. `01_missing_values_before.png` — missingness map before cleaning
2. `02_outlier_treatment_price.png` — unit price before/after outlier treatment
3. `03_revenue_by_category.png` — revenue by category
4. `04_monthly_revenue_trend.png` — monthly revenue trend
5. `05_region_payment_revenue.png` — revenue by region × payment method
6. `06_correlation_heatmap.png` — correlation matrix of numeric features
7. `07_age_vs_rating.png` — customer age vs. rating by category

## 7. Tools Used
Python, Pandas, NumPy, Matplotlib, Seaborn

## 8. How to Run
```bash
pip install pandas numpy matplotlib seaborn
python generate_raw_data.py       # creates raw_sales_data.csv
python data_cleaning_analysis.py  # cleans data + generates all plots
```

## 9. Files
- `raw_sales_data.csv` — raw input data
- `cleaned_sales_data.csv` — cleaned output data
- `generate_raw_data.py` — synthetic raw data generator
- `data_cleaning_analysis.py` — full cleaning + visualization pipeline
- `plots/` — all output charts
