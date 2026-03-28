import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import plotly.express as px

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
#
#   INFLATION ADJUSTMENT:
#     Higher inflation → higher mortgage rates → higher cost of capital.
#     We model this by adding the inflation rate directly to the base
#     cost-of-capital component (3%), which raises the overall rule threshold.
#     Example: 3% inflation → 6% rule.  5% inflation → 8% rule.
#
#   CRASH SCENARIO:
#     Simulates a housing price decline of 10%, 20%, or 30%.
#     This lowers median_price, which lowers the break-even rent,
#     which makes buying look relatively MORE expensive vs. renting —
#     showing users which counties flip from BUY to RENT under a crash.
# =============================================================================

# --- Configuration -----------------------------------------------------------

INPUT_FILE         = "fake_data.csv"
OUTPUT_CSV         = "five_percent_rule_results.csv"
OUTPUT_CHART_ALL   = "five_percent_rule_all_states.png"
OUTPUT_CHART_IDAHO = "five_percent_rule_idaho.png"

# Base 5% rule components (as decimals)
BASE_PROPERTY_TAX  = 0.01   # ~1% property tax
BASE_MAINTENANCE   = 0.01   # ~1% maintenance
BASE_COST_CAPITAL  = 0.03   # ~3% cost of capital (normal conditions)


# =============================================================================
# USER INPUTS
# =============================================================================

def get_inflation_rate():
    print("\n" + "=" * 60)
    print("  INFLATION RATE")
    print("=" * 60)
    print("  Enter the annual inflation rate you want to model.")
    print("  This raises the cost-of-capital component of the 5% rule.")
    print("  Examples:")
    print("    0    → Normal conditions (standard 5% rule)")
    print("    3    → Moderate inflation (raises rule to ~8%)")
    print("    5    → High inflation    (raises rule to ~10%)")
    print("    8    → Severe inflation  (raises rule to ~13%)")
    print("-" * 60)
    while True:
        try:
            val = float(input("  Enter inflation rate (% as a number, e.g. 3 for 3%): ").strip())
            if val < 0:
                print("  Please enter a non-negative number.")
                continue
            return val / 100  # Convert to decimal
        except ValueError:
            print("  Invalid input. Please enter a number.")


def get_crash_scenario():
    print("\n" + "=" * 60)
    print("  CRASH SCENARIO")
    print("=" * 60)
    print("  Simulate a housing market crash by applying a price decline")
    print("  to all median home prices before running the analysis.")
    print("-" * 60)
    print("  Options:")
    print("    0 → No crash (use current prices)")
    print("    1 → Mild crash    (-10% home prices)")
    print("    2 → Moderate crash (-20% home prices)")
    print("    3 → Severe crash   (-30% home prices)")
    print("-" * 60)
    while True:
        choice = input("  Enter option (0, 1, 2, or 3): ").strip()
        if choice == "0":
            return 0.0, "No crash"
        elif choice == "1":
            return 0.10, "Mild crash (-10%)"
        elif choice == "2":
            return 0.20, "Moderate crash (-20%)"
        elif choice == "3":
            return 0.30, "Severe crash (-30%)"
        else:
            print("  Invalid choice. Please enter 0, 1, 2, or 3.")


# =============================================================================
# MAIN
# =============================================================================

def main():

    # --- Get user inputs -----------------------------------------------------
    inflation_rate = get_inflation_rate()
    crash_pct, crash_label = get_crash_scenario()

    # --- Compute the adjusted rule threshold ---------------------------------
    # Inflation raises the cost-of-capital component on top of the base 3%
    adjusted_cost_capital = BASE_COST_CAPITAL + inflation_rate
    adjusted_rule_pct     = BASE_PROPERTY_TAX + BASE_MAINTENANCE + adjusted_cost_capital

    print("\n" + "=" * 60)
    print("  SCENARIO SUMMARY")
    print("=" * 60)
    print(f"  Inflation rate assumed   : {inflation_rate*100:.1f}%")
    print(f"  Crash scenario           : {crash_label}")
    print(f"  Base rule threshold      : 5.0% (property tax 1% + maintenance 1% + capital 3%)")
    print(f"  Inflation surcharge      : +{inflation_rate*100:.1f}% added as extra buyer cost")
    print(f"  Net effect               : buying threshold effectively {5+inflation_rate*100:.1f}% of home price")
    print("=" * 60)

    # --- Load & validate data ------------------------------------------------
    df = pd.read_csv(INPUT_FILE)
    df["fips"] = df["fips"].astype(str).str.zfill(5)

    original_count = len(df)
    df = df.dropna(subset=["rent_2br", "median_price"])
    dropped = original_count - len(df)
    if dropped > 0:
        print(f"\n  Note: Dropped {dropped} rows with missing data.")

    # --- Core calculations ---------------------------------------------------

    # CRASH SCENARIO: apply price decline to the purchase price only.
    # Cheaper homes → lower monthly ownership cost → buying looks MORE attractive.
    if crash_pct > 0:
        df["adjusted_price"] = df["median_price"] * (1 - crash_pct)
        print(f"\n  Note: Purchase price reduced by {crash_pct*100:.0f}% to simulate crash. "
              f"Rent is unchanged — buying becomes relatively more attractive.")
    else:
        df["adjusted_price"] = df["median_price"]

    # INFLATION SCENARIO: inflation raises the buyer's cost of capital, making
    # ownership more expensive. We add this as an extra monthly burden on the
    # buyer so the gap correctly widens AGAINST buying under high inflation.
    #
    # Extra monthly cost = adjusted_price * inflation_rate / 12
    df["inflation_cost"] = (df["adjusted_price"] * inflation_rate) / 12

    # Break-even rent = base 5% rule on crash-adjusted price.
    # effective_breakeven adds the inflation cost on top, so high inflation
    # correctly makes buying look LESS attractive.
    df["breakeven_rent"]      = (df["adjusted_price"] * 0.05) / 12
    df["effective_breakeven"] = df["breakeven_rent"] + df["inflation_cost"]

    # monthly_gap: positive = buying cheaper, negative = renting cheaper.
    df["monthly_gap"] = df["rent_2br"] - df["effective_breakeven"]

    def assign_verdict(gap):
        if gap > 50:
            return "BUY"
        elif gap < -50:
            return "RENT"
        else:
            return "BORDERLINE"

    df["verdict"] = df["monthly_gap"].apply(assign_verdict)

    # --- Print summary table -------------------------------------------------
    scenario_header = (f"Inflation: {inflation_rate*100:.1f}%  |  "
                       f"Crash: {crash_label}  |  "
                       f"Rule Threshold: {adjusted_rule_pct*100:.1f}%")

    print("\n" + "=" * 75)
    print("  5% RULE: RENT VS. BUY RESULTS BY COUNTY")
    print(f"  {scenario_header}")
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

    # --- Summary statistics --------------------------------------------------
    total      = len(df)
    buy_count  = (df["verdict"] == "BUY").sum()
    rent_count = (df["verdict"] == "RENT").sum()
    border     = (df["verdict"] == "BORDERLINE").sum()

    print(f"\n  Total counties analyzed : {total}")
    print(f"  BUY  verdict            : {buy_count}  ({buy_count/total*100:.1f}%)")
    print(f"  RENT verdict            : {rent_count}  ({rent_count/total*100:.1f}%)")
    print(f"  BORDERLINE              : {border}  ({border/total*100:.1f}%)")

    # --- Idaho-specific summary ----------------------------------------------
    idaho = df[df["state"] == "Idaho"].sort_values("monthly_gap", ascending=False)
    if not idaho.empty:
        print("\n" + "=" * 75)
        print("  IDAHO COUNTIES — RANKED BEST TO WORST FOR BUYING")
        print(f"  {scenario_header}")
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

    # --- Save results to CSV -------------------------------------------------
    output_cols = ["fips", "state", "county", "rent_2br", "median_price",
                   "breakeven_rent", "monthly_gap", "verdict"]
    df[output_cols].sort_values(["state", "county"]).to_csv(OUTPUT_CSV, index=False)
    print(f"\n  Results saved to: {OUTPUT_CSV}")

    # --- Chart 1: All states bar chart ---------------------------------------
    state_summary = (
        df.groupby("state")
          .agg(avg_gap=("monthly_gap", "mean"), county_count=("county", "count"))
          .reset_index()
          .sort_values("avg_gap", ascending=False)
    )

    colors = ["steelblue" if g >= 0 else "tomato" for g in state_summary["avg_gap"]]

    fig, ax = plt.subplots(figsize=(18, 8))
    ax.bar(state_summary["state"], state_summary["avg_gap"], color=colors,
           edgecolor="white", linewidth=0.5)
    ax.axhline(0, color="black", linewidth=1.0, linestyle="--")
    ax.set_title(
        f"5% Rule: Average Monthly Rent vs. Buy Gap by State\n"
        f"({scenario_header})",
        fontsize=12
    )
    ax.set_xlabel("State")
    ax.set_ylabel(f"Avg Monthly Gap ($/mo)  [Actual Rent − Break-even Rent @ {adjusted_rule_pct*100:.1f}% rule]")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:+,.0f}"))
    plt.xticks(rotation=90, fontsize=7)
    plt.tight_layout()
    plt.savefig(OUTPUT_CHART_ALL, dpi=150)
    plt.show()
    print(f"  Chart saved to: {OUTPUT_CHART_ALL}")

    # --- Chart 2: Idaho horizontal bar chart ---------------------------------
    if not idaho.empty:
        idaho_sorted   = idaho.sort_values("monthly_gap")
        colors_idaho   = ["steelblue" if g >= 0 else "tomato" for g in idaho_sorted["monthly_gap"]]

        fig, ax = plt.subplots(figsize=(10, max(6, len(idaho_sorted) * 0.35)))
        ax.barh(idaho_sorted["county"], idaho_sorted["monthly_gap"],
                color=colors_idaho, edgecolor="white")
        ax.axvline(0, color="black", linewidth=1.0, linestyle="--")
        ax.set_title(
            f"5% Rule: Rent vs. Buy Gap — Idaho Counties\n"
            f"({scenario_header})",
            fontsize=11
        )
        ax.set_xlabel(f"Monthly Gap ($/mo)  [Actual Rent − Break-even Rent @ {adjusted_rule_pct*100:.1f}% rule]")
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:+,.0f}"))
        plt.tight_layout()
        plt.savefig(OUTPUT_CHART_IDAHO, dpi=150)
        plt.show()
        print(f"  Chart saved to: {OUTPUT_CHART_IDAHO}")

    # --- Chart 3: USA choropleth map -----------------------------------------

    # Recalculate color scale bounds AFTER all scenario adjustments so the
    # map colors actually reflect the updated monthly_gap distribution.
    # Using a symmetric scale anchored at 0 ensures green/red stay meaningful:
    # green = buying cheaper, red = renting cheaper, yellow = break-even.
    gap_abs_max = max(abs(df["monthly_gap"].quantile(0.05)),
                      abs(df["monthly_gap"].quantile(0.95)))

    fig_map = px.choropleth(
        df,
        geojson="https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json",
        locations="fips",
        color="monthly_gap",
        color_continuous_scale="RdYlGn",
        range_color=[-gap_abs_max, gap_abs_max],  # symmetric so 0 = yellow always
        scope="usa",
        hover_data={"county": True, "state": True, "rent_2br": True, "median_price": True,
                    "effective_breakeven": True, "monthly_gap": True, "verdict": True},
        labels={
            "monthly_gap":    "Monthly Gap ($)",
            "rent_2br":       "Actual Rent",
            "median_price":   "Median Home Price",
            "effective_breakeven": "Break-even Rent (incl. inflation cost)",
        },
        title=(f"5% Rule: Rent vs. Buy by County (Green = Buy | Red = Rent)<br>"
               f"<sup>{scenario_header}</sup>")
    )

    fig_map.update_layout(
        coloraxis_colorbar=dict(
            title="Monthly Gap ($)",
            tickprefix="$",
        )
    )

    fig_map.show()
    print("  Choropleth map displayed.")


# =============================================================================
if __name__ == "__main__":
    main()