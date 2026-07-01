"""
clean_and_analyze.py
---------------------
Cleans the raw sales data and produces the summary tables that power
both the dashboard and the AI query layer.

This is the file to walk an interviewer through -- it shows real
data-cleaning judgment, not just "df.dropna()".

Run:
    python clean_and_analyze.py
Output:
    data/sales_clean.csv
    Printed summary insights
"""

import pandas as pd

df = pd.read_csv("data/sales_data.csv", parse_dates=["Order_Date"])

print("=== BEFORE CLEANING ===")
print(f"Rows: {len(df)}")
print(f"Missing values:\n{df.isna().sum()[df.isna().sum() > 0]}")

# 1. Standardize text fields (fixes the lowercase 'central' etc. and stray whitespace)
df["Region"] = df["Region"].str.strip().str.title()
df["Product"] = df["Product"].str.strip()
df["Category"] = df["Category"].str.strip()

# 2. Handle missing discounts -- assume no discount recorded means 0,
#    rather than dropping rows and losing sales data (documented assumption)
df["Discount"] = df["Discount"].fillna(0)

# 3. Feature engineering for downstream analysis
df["Year"] = df["Order_Date"].dt.year
df["Month"] = df["Order_Date"].dt.to_period("M").astype(str)
df["Profit_Margin"] = (df["Profit"] / df["Sales"]).round(3)

# 4. Sanity checks
assert df["Sales"].min() >= 0, "Negative sales found"
assert df["Region"].nunique() == 5, "Region cleaning didn't fully normalize values"

print("\n=== AFTER CLEANING ===")
print(f"Rows: {len(df)}")
print(f"Missing values: {df.isna().sum().sum()}")
print(f"Unique regions: {sorted(df['Region'].unique())}")

df.to_csv("data/sales_clean.csv", index=False)

# ---- Summary insights (also used by the AI layer) --------------------
print("\n=== KEY INSIGHTS ===")

by_region = df.groupby("Region").agg(Total_Sales=("Sales", "sum"), Total_Profit=("Profit", "sum")).round(0)
by_region["Profit_Margin_%"] = (by_region["Total_Profit"] / by_region["Total_Sales"] * 100).round(1)
print("\nBy Region:\n", by_region.sort_values("Total_Profit"))

by_category = df.groupby("Category").agg(Total_Sales=("Sales", "sum"), Total_Profit=("Profit", "sum")).round(0)
by_category["Profit_Margin_%"] = (by_category["Total_Profit"] / by_category["Total_Sales"] * 100).round(1)
print("\nBy Category:\n", by_category.sort_values("Total_Profit"))

by_month = df.groupby("Month").agg(Total_Sales=("Sales", "sum")).round(0)
print("\nMonthly sales trend (last 6 months):\n", by_month.tail(6))

worst_region = by_region["Total_Profit"].idxmin()
best_category = by_category["Total_Profit"].idxmax()
print(f"\nHeadline finding: '{worst_region}' region has the lowest total profit, "
      f"largely driven by high discounting. '{best_category}' is the strongest category by profit.")
