import pandas as pd
import os

# Folder where your CSV files are stored
folder = r"c:\Users\HP\Desktop\infosys\hourly"

# List of coins to process
coins = [
    "dogecoin",    # DOGE
    "ripple",      # XRP
    "polygon",     # MATIC
    "bitcoin",     # BTC
    "ethereum",    # ETH
    "litecoin",    # LTC
    "bitcoin_cash", # BCH
    "binance",     # BNB
    "polkadot",    # DOT
    "chainlink"    # LINK
]

# Columns to check for >= 1 INR
price_cols = ["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]

# Process each coin
for coin in coins:
    # Find all CSV files for this coin (hourly or daily)
    coin_files = [f for f in os.listdir(folder) if f.lower().startswith(coin) and f.endswith(".csv")]

    if not coin_files:
        print(f"No CSV files found for {coin}. Skipping.")
        continue

    for file in coin_files:
        file_path = os.path.join(folder, file)
        df = pd.read_csv(file_path)

        # Convert DATE column to datetime safely if exists
        if 'DATE' in df.columns:
            df['DATE'] = pd.to_datetime(df['DATE'], dayfirst=True, errors='coerce')
            df = df.dropna(subset=['DATE'])

        # Keep only rows where all OHLC and VOLUME values are >= 1
        df_filtered = df[(df[price_cols] >= 1).all(axis=1)]

        # Overwrite the same file
        df_filtered.to_csv(file_path, index=False)

        print(f"{file} filtered and overwritten ({len(df_filtered)} rows kept).")
