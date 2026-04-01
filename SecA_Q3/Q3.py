import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

DATA_PATH = "../bmw_global_sales_2018_2025.csv"
OUTPUT_DIR = Path("q3_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# =========================
# Load and clean
# =========================
df = pd.read_csv(DATA_PATH)

numeric_cols = [
    "Year", "Month", "Units_Sold", "Avg_Price_EUR",
    "Revenue_EUR", "BEV_Share", "Premium_Share",
    "GDP_Growth", "Fuel_Price_Index"
]

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df_q3 = df.dropna(subset=[
    "Month", "Region", "Units_Sold", "Revenue_EUR",
    "GDP_Growth", "Fuel_Price_Index"
]).copy()

df_q3["Month"] = df_q3["Month"].astype(int)

# =========================
# Aggregate by Region + Month
# =========================
region_month = (
    df_q3.groupby(["Region", "Month"], as_index=False)
    .agg(
        Units_Sold=("Units_Sold", "sum"),
        Revenue_EUR=("Revenue_EUR", "sum"),
        GDP_Growth=("GDP_Growth", "mean"),
        Fuel_Price_Index=("Fuel_Price_Index", "mean")
    )
    .sort_values(["Region", "Month"])
)

region_month.to_csv(OUTPUT_DIR / "region_month_summary.csv", index=False)

# =========================
# Monthly overall pattern
# =========================
monthly_overall = (
    df_q3.groupby("Month", as_index=False)
    .agg(
        Units_Sold=("Units_Sold", "sum"),
        Revenue_EUR=("Revenue_EUR", "sum"),
        GDP_Growth=("GDP_Growth", "mean"),
        Fuel_Price_Index=("Fuel_Price_Index", "mean")
    )
    .sort_values("Month")
)

monthly_overall.to_csv(OUTPUT_DIR / "monthly_overall_summary.csv", index=False)

# Peak / trough months
peak_units_month = monthly_overall.loc[monthly_overall["Units_Sold"].idxmax(), "Month"]
low_units_month = monthly_overall.loc[monthly_overall["Units_Sold"].idxmin(), "Month"]

peak_revenue_month = monthly_overall.loc[monthly_overall["Revenue_EUR"].idxmax(), "Month"]
low_revenue_month = monthly_overall.loc[monthly_overall["Revenue_EUR"].idxmin(), "Month"]

# =========================
# Correlation by region
# =========================
corr_rows = []
for region, g in region_month.groupby("Region"):
    corr_rows.append({
        "Region": region,
        "Units_vs_GDP": g["Units_Sold"].corr(g["GDP_Growth"]),
        "Units_vs_Fuel": g["Units_Sold"].corr(g["Fuel_Price_Index"]),
        "Revenue_vs_GDP": g["Revenue_EUR"].corr(g["GDP_Growth"]),
        "Revenue_vs_Fuel": g["Revenue_EUR"].corr(g["Fuel_Price_Index"])
    })

corr_df = pd.DataFrame(corr_rows)
corr_df.to_csv(OUTPUT_DIR / "region_macro_correlation_summary.csv", index=False)

print("=== Monthly overall summary ===")
print(monthly_overall)

print("\n=== Region-level macro correlation summary ===")
print(corr_df)

# =========================
# Plot 1: Units Sold by Month and Region
# =========================
plt.figure(figsize=(10, 6))
for region, g in region_month.groupby("Region"):
    plt.plot(g["Month"], g["Units_Sold"], marker="o", label=region)

plt.title("Monthly Units Sold by Region")
plt.xlabel("Month")
plt.ylabel("Total Units Sold")
plt.xticks(range(1, 13))
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "monthly_units_by_region.png", dpi=200)
plt.close()

# =========================
# Plot 2: Revenue by Month and Region
# =========================
plt.figure(figsize=(10, 6))
for region, g in region_month.groupby("Region"):
    plt.plot(g["Month"], g["Revenue_EUR"], marker="o", label=region)

plt.title("Monthly Revenue by Region")
plt.xlabel("Month")
plt.ylabel("Total Revenue (EUR)")
plt.xticks(range(1, 13))
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "monthly_revenue_by_region.png", dpi=200)
plt.close()

# =========================
# Plot 3: Overall monthly Units Sold
# =========================
plt.figure(figsize=(10, 6))
plt.plot(monthly_overall["Month"], monthly_overall["Units_Sold"], marker="o")
plt.title("Overall Monthly Units Sold")
plt.xlabel("Month")
plt.ylabel("Total Units Sold")
plt.xticks(range(1, 13))
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "overall_monthly_units.png", dpi=200)
plt.close()

# =========================
# Plot 4: Overall monthly Revenue
# =========================
plt.figure(figsize=(10, 6))
plt.plot(monthly_overall["Month"], monthly_overall["Revenue_EUR"], marker="o")
plt.title("Overall Monthly Revenue")
plt.xlabel("Month")
plt.ylabel("Total Revenue (EUR)")
plt.xticks(range(1, 13))
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "overall_monthly_revenue.png", dpi=200)
plt.close()

# =========================
# Pivot tables for easier interpretation
# =========================
units_pivot = region_month.pivot(index="Month", columns="Region", values="Units_Sold")
revenue_pivot = region_month.pivot(index="Month", columns="Region", values="Revenue_EUR")

units_pivot.to_csv(OUTPUT_DIR / "units_month_region_pivot.csv")
revenue_pivot.to_csv(OUTPUT_DIR / "revenue_month_region_pivot.csv")

# =========================
# Short summary text
# =========================
summary_lines = []
summary_lines.append("Question C Summary")
summary_lines.append("==================")
summary_lines.append("")
summary_lines.append(f"Peak month for Units_Sold: {peak_units_month}")
summary_lines.append(f"Lowest month for Units_Sold: {low_units_month}")
summary_lines.append(f"Peak month for Revenue_EUR: {peak_revenue_month}")
summary_lines.append(f"Lowest month for Revenue_EUR: {low_revenue_month}")
summary_lines.append("")
summary_lines.append("Region-level macro correlations:")
for _, row in corr_df.iterrows():
    summary_lines.append(
        f"- {row['Region']}: "
        f"Units~GDP={row['Units_vs_GDP']:.3f}, "
        f"Units~Fuel={row['Units_vs_Fuel']:.3f}, "
        f"Revenue~GDP={row['Revenue_vs_GDP']:.3f}, "
        f"Revenue~Fuel={row['Revenue_vs_Fuel']:.3f}"
    )

with open(OUTPUT_DIR / "q3_summary.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(summary_lines))

print(f"\nOutputs saved to: {OUTPUT_DIR.resolve()}")