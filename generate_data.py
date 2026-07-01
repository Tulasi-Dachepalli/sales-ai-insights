"""
generate_data.py
-----------------
Generates a realistic synthetic retail sales dataset for the
AI-Powered Sales Insights Assistant project.

Why synthetic data? It lets us control realistic patterns (seasonality,
regional performance gaps, a Q3 dip, a couple of underperforming
categories) so the analysis and AI layer have genuine, explainable
insights to surface -- exactly what you'd talk through in an interview.

Run:
    python generate_data.py
Output:
    data/sales_data.csv
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

# ---- Reference data -------------------------------------------------
REGIONS = ["North", "South", "East", "West", "Central"]
CATEGORIES = {
    "Electronics": ["Headphones", "Smartphone", "Laptop", "Smartwatch", "Tablet"],
    "Apparel": ["T-Shirt", "Jeans", "Jacket", "Sneakers", "Cap"],
    "Home & Kitchen": ["Blender", "Cookware Set", "Vacuum Cleaner", "Air Fryer", "Lamp"],
    "Beauty": ["Face Wash", "Moisturizer", "Lipstick", "Perfume", "Shampoo"],
    "Sports": ["Yoga Mat", "Dumbbell Set", "Cricket Bat", "Running Shoes", "Water Bottle"],
}
SEGMENTS = ["Consumer", "Corporate", "Small Business"]

# Deliberate performance biases so the data tells a real story
REGION_BIAS = {"North": 1.15, "South": 0.85, "East": 1.05, "West": 1.20, "Central": 0.75}
CATEGORY_BIAS = {
    "Electronics": 1.30, "Apparel": 0.95, "Home & Kitchen": 1.05,
    "Beauty": 0.90, "Sports": 0.80,
}

N_ROWS = 6000
start_date = datetime(2024, 1, 1)
end_date = datetime(2026, 6, 30)
date_range_days = (end_date - start_date).days

rows = []
order_id_counter = 100000

for i in range(N_ROWS):
    order_date = start_date + timedelta(days=int(np.random.uniform(0, date_range_days)))

    # Seasonality: boost Nov-Dec (holiday), dip in Jul-Aug
    month = order_date.month
    seasonal_factor = 1.0
    if month in (11, 12):
        seasonal_factor = 1.35
    elif month in (7, 8):
        seasonal_factor = 0.75

    region = np.random.choice(REGIONS)
    category = np.random.choice(list(CATEGORIES.keys()))
    product = np.random.choice(CATEGORIES[category])
    segment = np.random.choice(SEGMENTS, p=[0.55, 0.30, 0.15])

    base_price = {
        "Electronics": np.random.uniform(40, 900),
        "Apparel": np.random.uniform(10, 90),
        "Home & Kitchen": np.random.uniform(15, 250),
        "Beauty": np.random.uniform(5, 60),
        "Sports": np.random.uniform(8, 150),
    }[category]

    quantity = np.random.randint(1, 6)
    discount = np.random.choice([0, 0.05, 0.10, 0.15, 0.20, 0.30], p=[0.35, 0.2, 0.2, 0.15, 0.07, 0.03])

    unit_price = round(base_price, 2)
    sales = round(unit_price * quantity * (1 - discount) * REGION_BIAS[region] * CATEGORY_BIAS[category] * seasonal_factor, 2)

    # Cost ratio varies by category (Electronics has thinner base margin)
    cost_ratio = {"Electronics": 0.78, "Apparel": 0.55, "Home & Kitchen": 0.62, "Beauty": 0.45, "Sports": 0.58}[category]
    cost = round(sales * cost_ratio, 2)
    profit = round(sales - cost, 2)

    # Central region + high discounts occasionally push profit negative (realistic pain point)
    if region == "Central" and discount >= 0.20 and np.random.rand() < 0.6:
        profit = round(profit - np.random.uniform(20, 120), 2)

    order_id_counter += 1
    rows.append({
        "Order_ID": f"ORD-{order_id_counter}",
        "Order_Date": order_date.strftime("%Y-%m-%d"),
        "Region": region,
        "Segment": segment,
        "Category": category,
        "Product": product,
        "Quantity": quantity,
        "Unit_Price": unit_price,
        "Discount": discount,
        "Sales": sales,
        "Profit": profit,
    })

df = pd.DataFrame(rows).sort_values("Order_Date").reset_index(drop=True)

# Introduce a small amount of realistic messiness for the cleaning step
# (this is what you'll show off in your data-cleaning code / interview talk track)
messy_idx = np.random.choice(df.index, size=60, replace=False)
df.loc[messy_idx[:20], "Discount"] = np.nan
df.loc[messy_idx[20:40], "Region"] = df.loc[messy_idx[20:40], "Region"].str.lower()
df.loc[messy_idx[40:60], "Product"] = df.loc[messy_idx[40:60], "Product"] + "  "  # trailing whitespace

df.to_csv("data/sales_data.csv", index=False)
print(f"Generated {len(df)} rows -> data/sales_data.csv")
print(df.head())
