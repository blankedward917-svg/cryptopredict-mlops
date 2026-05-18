# Dataset Architecture

The project keeps the complete cryptocurrency dataset and all supported coins. No dataset or model artifact is intentionally removed for the clean MLOps implementation.

## Supported Coins

The production app serves 13 symbols:

`BTC`, `ETH`, `DOGE`, `LTC`, `DOT`, `MATIC`, `XRP`, `LINK`, `BCH`, `BNB`, `SOL`, `ADA`, `AVAX`

Some folders also contain alias files such as `matic`/`polygon` and `xrp`/`ripple`, plus merged all-coin files. These are retained.

## Directory Meaning

| Location | Purpose | Expected role |
| --- | --- | --- |
| `milestone-1/daily` | Raw/raw-ish daily OHLCV history | Immutable source data |
| `milestone-1/hourly` | Raw/raw-ish hourly OHLCV history | Immutable source data |
| `milestone-2/infosys/cleaned data/daily` | Cleaned daily OHLCV | Canonical training data |
| `milestone-2/infosys/cleaned data/hourly` | Cleaned hourly OHLCV | Canonical training data |
| `live_data/daily` | Live/synced working copy | Monitoring/demo input |
| `live_data/hourly` | Live/synced working copy | Monitoring/demo input |
| `milestone-2/infosys/outputs/models` | Keras LSTM models | Model serving and registry artifacts |
| `milestone-2/infosys/outputs/scalers` | MinMax scalers | Inference preprocessing artifacts |
| `milestone-2/infosys/outputs/predictions` | Validation/test predictions | Evaluation artifacts |
| `milestone-2/infosys/outputs/metrics` | RMSE/MAE/MAPE metrics | Experiment comparison artifacts |
| `backened/crypto_pro.db` | SQLite serving database | Centralized recent OHLCV, users, predictions, trades |

## Current Inventory

Generate the inventory:

```powershell
python scripts/dataset_inventory.py
```

Generated files:

- `reports/inventory/dataset_inventory.csv`
- `reports/inventory/artifact_inventory.csv`
- `reports/inventory/db_ohlcv_inventory.csv`
- `reports/inventory/dataset_inventory.md`

Latest generated summary:

- `milestone-1` raw daily: 16 CSV files, 93,488 rows
- `milestone-1` raw hourly: 16 CSV files, 2,439,980 rows
- `milestone-2` cleaned daily: 14 CSV files, 68,236 rows
- `milestone-2` cleaned hourly: 14 CSV files, 1,794,819 rows
- `live_data` daily: 16 CSV files, 59,290 rows
- `live_data` hourly: 16 CSV files, 1,468,312 rows

## Live Data Clarification

`live_data` is not just the last 100 days for the historical CSV files. For BTC, the generated inventory shows:

- `live_data/daily/btc_inr_daily.csv`: 2010-07-17 to 2026-03-15
- `live_data/hourly/btc_inr_hourly.csv`: 2010-07-17 to 2026-03-15 14:00 UTC

The "last 100 days" behavior applies to the centralized SQLite `ohlcv` sync fallback in `backened/data_sync.py` when a coin/timeframe is new or underfilled. The generated DB inventory shows the SQLite serving table currently contains recent windows through 2026-05-16:

- daily rows: roughly 101 rows per coin
- hourly rows: roughly 2,209 rows per coin

## Retention Check

Run:

```powershell
python scripts/validate_retention.py
```

This verifies every supported coin has:

- milestone-1 raw daily/hourly files
- live daily/hourly files
- milestone-2 cleaned daily/hourly files
- daily/hourly Keras models
- daily/hourly scalers

The generated report is `reports/inventory/retention_check.csv`.
