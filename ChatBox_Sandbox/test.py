import pandas as pd

df = pd.read_csv("ChatBox_Sandbox/complete_county_housing_buy_vs_rent.csv")
df = df.dropna(subset=["rent", "median_price"])

df["breakeven"] = (df["median_price"] * 0.05) / 12
df["gap"] = df["rent"] - df["breakeven"]

print(f"Median rent:        ${df['rent'].median():,.0f}")
print(f"Median home price:  ${df['median_price'].median():,.0f}")
print(f"Median break-even:  ${df['breakeven'].median():,.0f}")
print(f"Median gap:         ${df['gap'].median():+,.0f}")
print(f"\nBUY counties:       {(df['gap'] > 50).sum()}")
print(f"RENT counties:      {(df['gap'] < -50).sum()}")
print(f"BORDERLINE:         {((df['gap'] >= -50) & (df['gap'] <= 50)).sum()}")
print(f"\nSample P2R ratios:")
print((df['median_price'] / (df['rent'] * 12)).describe().round(1))