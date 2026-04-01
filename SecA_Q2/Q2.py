import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

DATA_PATH = "../bmw_global_sales_2018_2025.csv"
OUTPUT_DIR = Path("q2_outputs")
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

df = df.dropna(subset=["Model", "Units_Sold", "Avg_Price_EUR", "GDP_Growth"]).copy()
df = df[(df["Units_Sold"] > 0) & (df["Avg_Price_EUR"] > 0)].copy()

# Log transform for stable elasticity approximation
df["log_units"] = np.log(df["Units_Sold"])
df["log_price"] = np.log(df["Avg_Price_EUR"])

# GDP bucket
df["GDP_Bucket"] = pd.qcut(
    df["GDP_Growth"],
    q=3,
    labels=["Low", "Medium", "High"],
    duplicates="drop"
)

def elasticity_slope(x, y):
    """
    Approximate price elasticity using a simple log-log slope:
    log(Units_Sold) ~ a + b * log(Avg_Price_EUR)
    """
    if len(x) < 2 or x.nunique() < 2:
        return np.nan
    return np.polyfit(x, y, 1)[0]

# =========================
# Overall model elasticity
# =========================
overall_rows = []
for model, g in df.groupby("Model"):
    overall_rows.append({
        "Model": model,
        "Elasticity_LogLog": elasticity_slope(g["log_price"], g["log_units"]),
        "Obs": len(g),
        "Price_Units_Corr": g["Avg_Price_EUR"].corr(g["Units_Sold"])
    })

overall_df = pd.DataFrame(overall_rows).sort_values("Elasticity_LogLog")
overall_df.to_csv(OUTPUT_DIR / "overall_model_elasticity.csv", index=False)

print("=== Overall model elasticity ===")
print(overall_df)

# =========================
# Elasticity by GDP bucket
# =========================
bucket_rows = []
for (model, bucket), g in df.groupby(["Model", "GDP_Bucket"]):
    bucket_rows.append({
        "Model": model,
        "GDP_Bucket": str(bucket),
        "Elasticity_LogLog": elasticity_slope(g["log_price"], g["log_units"]),
        "Obs": len(g),
        "Price_Units_Corr": g["Avg_Price_EUR"].corr(g["Units_Sold"])
    })

bucket_df = pd.DataFrame(bucket_rows).sort_values(["Model", "GDP_Bucket"])
bucket_df.to_csv(OUTPUT_DIR / "elasticity_by_gdp_bucket.csv", index=False)

print("\n=== Elasticity by GDP bucket ===")
print(bucket_df)

# =========================
# Plot 1: Overall elasticity by model
# =========================
plot_df = overall_df.sort_values("Elasticity_LogLog")

plt.figure(figsize=(10, 6))
plt.bar(plot_df["Model"], plot_df["Elasticity_LogLog"])
plt.axhline(0, linestyle="--", linewidth=1)
plt.title("Overall Price Elasticity by Model (Log-Log Approximation)")
plt.xlabel("Model")
plt.ylabel("Elasticity")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "overall_elasticity_bar.png", dpi=200)
plt.close()

# =========================
# Plot 2: Elasticity by GDP bucket
# =========================
pivot_df = bucket_df.pivot(index="Model", columns="GDP_Bucket", values="Elasticity_LogLog")

pivot_df.plot(kind="bar", figsize=(12, 6))
plt.axhline(0, linestyle="--", linewidth=1)
plt.title("Price Elasticity by Model and GDP Growth Bucket")
plt.xlabel("Model")
plt.ylabel("Elasticity")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "elasticity_by_gdp_bucket_bar.png", dpi=200)
plt.close()

# =========================
# Save short text summary
# =========================
negative_models = overall_df[overall_df["Elasticity_LogLog"] < 0].copy()

summary_lines = []
summary_lines.append("Question B Summary")
summary_lines.append("==================")
summary_lines.append("")
summary_lines.append("Method: log-log elasticity approximation")
summary_lines.append("Interpretation: more negative values imply stronger price sensitivity.")
summary_lines.append("")

summary_lines.append("Overall model ranking:")
for _, row in overall_df.iterrows():
    summary_lines.append(
        f"- {row['Model']}: elasticity={row['Elasticity_LogLog']:.3f}, obs={int(row['Obs'])}"
    )

summary_lines.append("")
summary_lines.append("Models with strongest negative elasticity:")
for _, row in negative_models.head(3).iterrows():
    summary_lines.append(
        f"- {row['Model']}: elasticity={row['Elasticity_LogLog']:.3f}"
    )

with open(OUTPUT_DIR / "q2_summary.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(summary_lines))

print(f"\nOutputs saved to: {OUTPUT_DIR.resolve()}")