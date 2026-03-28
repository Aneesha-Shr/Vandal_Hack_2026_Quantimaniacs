import pandas as pd
import numpy as np

# Assuming 'df' is your current DataFrame with 'state', 'county', and 'average_rent_price'
# Replace 'your_data.csv' with the actual name or path of your file
file_path = 'county_housing_buy_vs_rent.csv'

# Read the CSV file into a pandas DataFrame
df = pd.read_csv(file_path)
#df = df.drop(columns=['fips'])

# Display the first 5 rows to verify it loaded correctly
print(df.head())

# Optional: Check the data types and look for any missing values
print(df.info())

# 1. Define approximate Price-to-Rent ratios by state 
# (You can expand this dictionary based on the states in your CSV)
state_ratios = {
    'Idaho': 32.0,
    'California': 34.0,
    'Washington': 30.0,
    'Texas': 20.0,
    'Ohio': 12.0,
    'New York': 25.0
}

# National average fallback for states not in the dictionary
default_ratio = 23.0 

# 2. Map the ratio to the dataframe based on the 'state' column
df['p2r_ratio'] = df['state'].map(state_ratios).fillna(default_ratio)

# 3. Calculate the base simulated house price (Monthly Rent * 12 months * Ratio)
df['simulated_house_price'] = df['rent_2br'] * 12 * df['p2r_ratio']

# 4. Add Gaussian noise (e.g., 10% standard deviation) to simulate real-world market variance
# The 'loc=1.0' centers the multiplier at 100% of the calculated price
noise_multiplier = np.random.normal(loc=1.0, scale=0.10, size=len(df))
df['median_price'] = df['simulated_house_price'] * noise_multiplier

# Clean up the temporary calculation columns and round to whole dollars
df = df.drop(columns=['p2r_ratio', 'simulated_house_price'])
df['median_price'] = df['median_price'].round(0)

print(df.head())

df.to_csv('fake_data.csv', index=False)

print("Data successfully saved to fake_data.csv!")