import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

DATA_PATH = "../bmw_global_sales_2018_2025.csv"
OUTPUT_DIR = Path("q1_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# Load dataset
df = pd.read_csv(DATA_PATH)

# Basic cleaning
numeric_cols = [
    "Year", "Month", "Units_Sold", "Avg_Price_EUR",
    "Revenue_EUR", "BEV_Share", "Premium_Share",
    "GDP_Growth", "Fuel_Price_Index"
]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df_q1 = df.dropna(subset=["Year", "Region", "BEV_Share", "Units_Sold", "Revenue_EUR"]).copy()
df_q1["Year"] = df_q1["Year"].astype(int)

# Aggregate by Year + Region
year_region = (
    df_q1.groupby(["Year", "Region"], as_index=False)
    .agg(
        BEV_Share=("BEV_Share", "mean"),
        Units_Sold=("Units_Sold", "sum"),
        Revenue_EUR=("Revenue_EUR", "sum")
    )
    .sort_values(["Region", "Year"])
)

year_region.to_csv(OUTPUT_DIR / "year_region_summary.csv", index=False)

# Correlation + growth summary
results = []
for region, g in year_region.groupby("Region"):
    g = g.sort_values("Year")

    bev_units_corr = g["BEV_Share"].corr(g["Units_Sold"])
    bev_revenue_corr = g["BEV_Share"].corr(g["Revenue_EUR"])
    bev_start = g["BEV_Share"].iloc[0]
    bev_end = g["BEV_Share"].iloc[-1]
    bev_growth = bev_end - bev_start
    slope = np.polyfit(g["Year"], g["BEV_Share"], 1)[0]

    results.append({
        "Region": region,
        "BEV_Units_Corr": bev_units_corr,
        "BEV_Revenue_Corr": bev_revenue_corr,
        "BEV_Start": bev_start,
        "BEV_End": bev_end,
        "BEV_Growth_2018_2025": bev_growth,
        "BEV_Trend_Slope": slope
    })

corr_df = pd.DataFrame(results).sort_values("BEV_Growth_2018_2025", ascending=False)
corr_df.to_csv(OUTPUT_DIR / "region_correlation_summary.csv", index=False)

print("=== Region-level summary ===")
print(corr_df)

strongest_growth_region = corr_df.iloc[0]["Region"]
strongest_units_corr_region = corr_df.sort_values("BEV_Units_Corr", ascending=False).iloc[0]["Region"]
strongest_revenue_corr_region = corr_df.sort_values("BEV_Revenue_Corr", ascending=False).iloc[0]["Region"]

print("\nStrongest BEV growth region:", strongest_growth_region)
print("Strongest BEV vs Units_Sold correlation region:", strongest_units_corr_region)
print("Strongest BEV vs Revenue_EUR correlation region:", strongest_revenue_corr_region)

# Plot 1: BEV share over time
plt.figure(figsize=(10, 6))
for region, g in year_region.groupby("Region"):
    plt.plot(g["Year"], g["BEV_Share"], marker="o", label=region)
plt.title("BEV Share Over Time by Region")
plt.xlabel("Year")
plt.ylabel("Average BEV Share")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "bev_share_over_time.png", dpi=200)
plt.close()

# Plot 2: Units sold over time
plt.figure(figsize=(10, 6))
for region, g in year_region.groupby("Region"):
    plt.plot(g["Year"], g["Units_Sold"], marker="o", label=region)
plt.title("Units Sold Over Time by Region")
plt.xlabel("Year")
plt.ylabel("Total Units Sold")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "units_sold_over_time.png", dpi=200)
plt.close()

# Plot 3: Revenue over time
plt.figure(figsize=(10, 6))
for region, g in year_region.groupby("Region"):
    plt.plot(g["Year"], g["Revenue_EUR"], marker="o", label=region)
plt.title("Revenue Over Time by Region")
plt.xlabel("Year")
plt.ylabel("Total Revenue (EUR)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "revenue_over_time.png", dpi=200)
plt.close()

# Plot 4: BEV Share vs Units Sold
plt.figure(figsize=(10, 6))
for region, g in year_region.groupby("Region"):
    plt.scatter(g["BEV_Share"], g["Units_Sold"], label=region)
plt.title("BEV Share vs Units Sold")
plt.xlabel("Average BEV Share")
plt.ylabel("Total Units Sold")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "bev_vs_units.png", dpi=200)
plt.close()

# Plot 5: BEV Share vs Revenue
plt.figure(figsize=(10, 6))
for region, g in year_region.groupby("Region"):
    plt.scatter(g["BEV_Share"], g["Revenue_EUR"], label=region)
plt.title("BEV Share vs Revenue")
plt.xlabel("Average BEV Share")
plt.ylabel("Total Revenue (EUR)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "bev_vs_revenue.png", dpi=200)
plt.close()