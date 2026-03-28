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
    'Illinois': 20.3,
    'Texas': 20.3,
    'Florida': 20.4,
    'Mississippi': 20.7,
    'West Virginia': 21.4,
    'Michigan': 21.4,
    'Oklahoma': 21.7,
    'Pennsylvania': 21.9,
    'Louisiana': 22.0,
    'Indiana': 22.3,
    'Ohio': 22.3,
    'Kansas': 22.4,
    'Georgia': 22.6,
    'Arkansas': 22.6,
    'Iowa': 22.7,
    'Virginia': 23.0,
    'Alaska': 23.3,
    'New Mexico': 23.3,
    'Nebraska': 23.4,
    'South Carolina': 23.4,
    'Maryland': 23.4,
    'Missouri': 23.7,
    'Kentucky': 23.7,
    'Arizona': 23.8,
    'Alabama': 23.8,
    'Minnesota': 23.9,
    'North Carolina': 24.2,
    'North Dakota': 24.7,
    'Connecticut': 24.9,
    'Wisconsin': 24.9,
    'New York': 24.9,
    'Maine': 25.2,
    'Delaware': 25.5,
    'Vermont': 25.5,
    'Tennessee': 25.6,
    'New Jersey': 25.6,
    'Nevada': 25.8,
    'New Hampshire': 26.1,
    'Colorado': 27.9,
    'South Dakota': 28.3,
    'Wyoming': 29.0,
    'Rhode Island': 29.4,
    'Washington': 30.2,
    'Massachusetts': 30.2,
    'Oregon': 30.5,
    'Utah': 30.8,
    'Idaho': 32.1,
    'District Of Columbia': 33.0,
    'California': 33.2,
    'Montana': 34.1,
    'Hawaii': 40.0
}

# National average fallback for states not in the dictionary
default_ratio = 23.2

# 2. Map the ratio to the dataframe based on the 'state' column
df['p2r_ratio'] = df['state'].map(state_ratios).fillna(default_ratio)

# 3. Calculate the base simulated house price (Monthly Rent * 12 months * Ratio)
df['simulated_house_price'] = df['rent_2br'] * 12 * df['p2r_ratio']

# 4. Add Gaussian noise (e.g., 10% standard deviation) to simulate real-world market variance
# The 'loc=1.0' centers the multiplier at 100% of the calculated price
noise_multiplier = np.random.normal(loc=1.0, scale=0.30, size=len(df))
df['median_price'] = df['simulated_house_price'] * noise_multiplier

# Clean up the temporary calculation columns and round to whole dollars
df = df.drop(columns=['p2r_ratio', 'simulated_house_price'])
df['median_price'] = df['median_price'].round(0)

print(df.head())

df.to_csv('fake_data.csv', index=False)

print("Data successfully saved to fake_data.csv!")
