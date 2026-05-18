import pandas as pd
import os

# Folder where CSVs are stored
folder = r"c:\Users\HP\Desktop\infosys\daily"

# Pattern to identify hourly CSVs
csv_files = [f for f in os.listdir(folder) if f.endswith("_daily.csv")]

if not csv_files:
    print("No daily CSV files found in the folder. Exiting.")
    exit()

dfs = []

for file in csv_files:
    file_path = os.path.join(folder, file)
    df = pd.read_csv(file_path)

    # Infer cryptocurrency name from filename (before _inr_daily.csv)
    coin_name = file.split("_")[0].capitalize()
    df['Cryptocurrency'] = coin_name

    dfs.append(df)
    print(f"Loaded {file} with {len(df)} rows.")

# Merge all dataframes
merged_df = pd.concat(dfs, ignore_index=True)

# Convert DATE column to datetime safely
if 'DATE' in merged_df.columns:
    merged_df['DATE'] = pd.to_datetime(merged_df['DATE'], dayfirst=True, errors='coerce')
    merged_df = merged_df.dropna(subset=['DATE'])  # remove rows with invalid dates
    merged_df.sort_values(by=['DATE', 'Cryptocurrency'], inplace=True)

# Filter out rows where any price column < 1 INR
price_cols = ["OPEN", "HIGH", "LOW", "CLOSE"]
merged_df = merged_df[(merged_df[price_cols] >= 1).all(axis=1)]

# Save merged and filtered CSV
output_file = os.path.join(folder, "all_crypto_inr_hourly_merged.csv")
merged_df.to_csv(output_file, index=False)

print(f"All CSVs merged, filtered, and saved as {output_file} with {len(merged_df)} rows.")
