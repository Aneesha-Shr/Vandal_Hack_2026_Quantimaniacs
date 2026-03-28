import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# =============================================================================
# 5% RULE: RENT VS. BUY ANALYSIS BY COUNTY
# =============================================================================
# The 5% Rule (Ben Felix):
#   Break-even monthly rent = (Home Price x 5%) / 12
#
#   The 5% breaks down as:
#     ~1% property tax
#     ~1% maintenance / cost of ownership
#     ~3% cost of capital (opportunity cost + mortgage interest)
#
#   If actual rent < break-even rent → RENTING is cheaper
#   If actual rent > break-even rent → BUYING is cheaper
# =============================================================================

# --- Configuration -----------------------------------------------------------

INPUT_FILE         = "fake_data.csv"
OUTPUT_CSV         = "five_percent_rule_results.csv"
OUTPUT_CHART_ALL   = "five_percent_rule_all_states.png"
OUTPUT_CHART_IDAHO = "five_percent_rule_idaho.png"

FIVE_PCT_ANNUAL = 0.05   # The 5% rule constant

# --- Load & Validate Data ----------------------------------------------------

df = pd.read_csv(INPUT_FILE)

# Drop rows missing either rent or home price — can't run the rule without both
original_count = len(df)
df = df.dropna(subset=["rent_2br", "median_price"])
dropped = original_count - len(df)
if dropped > 0:
    print(f"  Note: Dropped {dropped} rows with missing rent or median price data.")

# --- Core 5% Rule Calculations -----------------------------------------------

# Break-even rent: the monthly cost of owning expressed as a rent equivalent
df["breakeven_rent"] = (df["median_price"] * FIVE_PCT_ANNUAL) / 12

# Monthly gap: positive = buying is cheaper, negative = renting is cheaper
df["monthly_gap"] = df["rent_2br"] - df["breakeven_rent"]

# Verdict — $50/mo buffer on each side to account for borderline cases
def assign_verdict(gap):
    if gap > 50:
        return "BUY"
    elif gap < -50:
        return "RENT"
    else:
        return "BORDERLINE"

df["verdict"] = df["monthly_gap"].apply(assign_verdict)

# --- Print Summary Table -----------------------------------------------------

print("\n" + "=" * 75)
print("  5% RULE: RENT VS. BUY RESULTS BY COUNTY")
print("=" * 75)
print(f"  {'State':<20} {'County':<28} {'Rent':>8} {'Break-even':>12} {'Gap':>8} {'Verdict'}")
print("-" * 75)

for _, row in df.sort_values(["state", "county"]).iterrows():
    print(
        f"  {row['state']:<20} {row['county']:<28} "
        f"${row['rent_2br']:>7,.0f} "
        f"${row['breakeven_rent']:>11,.0f} "
        f"${row['monthly_gap']:>+7,.0f} "
        f"{row['verdict']}"
    )

print("=" * 75)

# --- Summary Statistics ------------------------------------------------------

total      = len(df)
buy_count  = (df["verdict"] == "BUY").sum()
rent_count = (df["verdict"] == "RENT").sum()
border     = (df["verdict"] == "BORDERLINE").sum()

print(f"\n  Total counties analyzed : {total}")
print(f"  BUY  verdict            : {buy_count}  ({buy_count/total*100:.1f}%)")
print(f"  RENT verdict            : {rent_count}  ({rent_count/total*100:.1f}%)")
print(f"  BORDERLINE              : {border}  ({border/total*100:.1f}%)")

# --- Idaho-Specific Summary --------------------------------------------------

idaho = df[df["state"] == "Idaho"].sort_values("monthly_gap", ascending=False)
if not idaho.empty:
    print("\n" + "=" * 75)
    print("  IDAHO COUNTIES — RANKED BEST TO WORST FOR BUYING")
    print("  (Positive gap = buying is cheaper by that amount per month)")
    print("=" * 75)
    print(f"  {'County':<28} {'Rent':>8} {'Break-even':>12} {'Gap':>8} {'Verdict'}")
    print("-" * 75)
    for _, row in idaho.iterrows():
        print(
            f"  {row['county']:<28} "
            f"${row['rent_2br']:>7,.0f} "
            f"${row['breakeven_rent']:>11,.0f} "
            f"${row['monthly_gap']:>+7,.0f} "
            f"{row['verdict']}"
        )
    print("=" * 75)

# --- Save Results to CSV -----------------------------------------------------

output_cols = ["fips", "state", "county", "rent_2br", "median_price",
               "breakeven_rent", "monthly_gap", "verdict"]
df[output_cols].sort_values(["state", "county"]).to_csv(OUTPUT_CSV, index=False)
print(f"\n  Results saved to: {OUTPUT_CSV}")

# --- Chart 1: All States — Average Gap by State (Bar Chart) ------------------

state_summary = (
    df.groupby("state")
      .agg(avg_gap=("monthly_gap", "mean"), county_count=("county", "count"))
      .reset_index()
      .sort_values("avg_gap", ascending=False)
)

colors = ["steelblue" if g >= 0 else "tomato" for g in state_summary["avg_gap"]]

fig, ax = plt.subplots(figsize=(18, 8))
ax.bar(state_summary["state"], state_summary["avg_gap"], color=colors, edgecolor="white", linewidth=0.5)
ax.axhline(0, color="black", linewidth=1.0, linestyle="--")
ax.set_title(
    "5% Rule: Average Monthly Rent vs. Buy Gap by State\n"
    "(Blue = Buying cheaper on average  |  Red = Renting cheaper on average)",
    fontsize=13
)
ax.set_xlabel("State")
ax.set_ylabel("Avg Monthly Gap ($/mo)  [Actual Rent − Break-even Rent]")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:+,.0f}"))
plt.xticks(rotation=90, fontsize=7)
plt.tight_layout()
plt.savefig(OUTPUT_CHART_ALL, dpi=150)
plt.show()
print(f"  Chart saved to: {OUTPUT_CHART_ALL}")

# --- Chart 2: Idaho Counties — Horizontal Bar Chart -------------------------

if not idaho.empty:
    idaho_sorted = idaho.sort_values("monthly_gap")
    colors_idaho = ["steelblue" if g >= 0 else "tomato" for g in idaho_sorted["monthly_gap"]]

    fig, ax = plt.subplots(figsize=(10, max(6, len(idaho_sorted) * 0.35)))
    ax.barh(idaho_sorted["county"], idaho_sorted["monthly_gap"], color=colors_idaho, edgecolor="white")
    ax.axvline(0, color="black", linewidth=1.0, linestyle="--")
    ax.set_title(
        "5% Rule: Rent vs. Buy Gap — Idaho Counties\n"
        "(Blue = Buying cheaper  |  Red = Renting cheaper)",
        fontsize=12
    )
    ax.set_xlabel("Monthly Gap ($/mo)  [Actual Rent − Break-even Rent]")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:+,.0f}"))
    plt.tight_layout()
    plt.savefig(OUTPUT_CHART_IDAHO, dpi=150)
    plt.show()
    print(f"  Chart saved to: {OUTPUT_CHART_IDAHO}")
    
