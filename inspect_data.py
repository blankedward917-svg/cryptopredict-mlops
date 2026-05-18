import pandas as pd
import os

files = [
    'milestone-1/hourly/btc_inr_hourly.csv',
    'milestone-1/daily/btc_inr_daily.csv'
]

for f in files:
    if os.path.exists(f):
        df = pd.read_csv(f)
        min_ts = df.TIMESTAMP.min()
        max_ts = df.TIMESTAMP.max()
        print(f"File: {f}")
        print(f"  Min: {min_ts} ({pd.to_datetime(min_ts, unit='s')})")
        print(f"  Max: {max_ts} ({pd.to_datetime(max_ts, unit='s')})")
        print(f"  Rows: {len(df)}")
        print(f"  First 2 rows TIMESTAMP: {df.TIMESTAMP.iloc[:2].values}")
        print(f"  Last 2 rows TIMESTAMP: {df.TIMESTAMP.iloc[-2:].values}")
    else:
        print(f"File not found: {f}")
