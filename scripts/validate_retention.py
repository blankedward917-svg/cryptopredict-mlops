from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "reports" / "inventory" / "retention_check.csv"


COINS = {
    "BTC": {
        "m1": "btc_inr",
        "live": "btc_inr",
        "m2_daily": "bitcoin_inr_daily.csv",
        "m2_hourly": "bitcoin_inr_hourly.csv",
        "model": "BITCOIN_INR",
    },
    "ETH": {
        "m1": "eth_inr",
        "live": "eth_inr",
        "m2_daily": "ethereum_inr_daily.csv",
        "m2_hourly": "ethereum_inr_hourly.csv",
        "model": "ETHEREUM_INR",
    },
    "DOGE": {
        "m1": "doge_inr",
        "live": "doge_inr",
        "m2_daily": "dogecoin_inr_daily.csv",
        "m2_hourly": "dogecoin_inr_hourly.csv",
        "model": "DOGECOIN_INR",
    },
    "LTC": {
        "m1": "ltc_inr",
        "live": "ltc_inr",
        "m2_daily": "litecoin_inr_daily.csv",
        "m2_hourly": "litecoin_inr_hourly.csv",
        "model": "LITECOIN_INR",
    },
    "DOT": {
        "m1": "dot_inr",
        "live": "dot_inr",
        "m2_daily": "polkadot_inr_daily.csv",
        "m2_hourly": "polkadot_inr_hourly.csv",
        "model": "POLKADOT_INR",
    },
    "MATIC": {
        "m1": "polygon_inr",
        "live": "polygon_inr",
        "m2_daily": "polygon_inr_daily.csv",
        "m2_hourly": "polygon_inr_hourly.csv",
        "model": "POLYGON_INR",
    },
    "XRP": {
        "m1": "ripple_inr",
        "live": "ripple_inr",
        "m2_daily": "ripple_inr_daily.csv",
        "m2_hourly": "ripple_inr_hourly.csv",
        "model": "RIPPLE_INR",
    },
    "LINK": {
        "m1": "link_inr",
        "live": "link_inr",
        "m2_daily": "chainlink_coin_inr_daily.csv",
        "m2_hourly": "chainlink_inr_hourly.csv",
        "model": "CHAINLINK_INR",
        "daily_model_alt": "CHAINLINK_COIN_INR",
    },
    "BCH": {
        "m1": "bch_inr",
        "live": "bch_inr",
        "m2_daily": "bitcoin_cash_inr_daily.csv",
        "m2_hourly": "bitcoin_cash_inr_hourly.csv",
        "model": "BITCOIN_CASH_INR",
    },
    "BNB": {
        "m1": "bnb_inr",
        "live": "bnb_inr",
        "m2_daily": "binance_coin_inr_daily.csv",
        "m2_hourly": "binance_inr_hourly.csv",
        "model": "BINANCE_INR",
        "daily_model_alt": "BINANCE_COIN_INR",
    },
    "SOL": {
        "m1": "sol_inr",
        "live": "sol_inr",
        "m2_daily": "solana_inr_daily.csv",
        "m2_hourly": "solana_inr_hourly.csv",
        "model": "SOLANA_INR",
    },
    "ADA": {
        "m1": "ada_inr",
        "live": "ada_inr",
        "m2_daily": "cardano_inr_daily.csv",
        "m2_hourly": "cardano_inr_hourly.csv",
        "model": "CARDANO_INR",
    },
    "AVAX": {
        "m1": "avax_inr",
        "live": "avax_inr",
        "m2_daily": "avalanche_inr_daily.csv",
        "m2_hourly": "avalanche_inr_hourly.csv",
        "model": "AVALANCHE_INR",
    },
}


def path_status(label: str, path: Path) -> dict:
    return {
        "label": label,
        "path": str(path.relative_to(ROOT)),
        "exists": path.exists(),
        "size_mb": round(path.stat().st_size / (1024 * 1024), 3) if path.exists() and path.is_file() else 0,
    }


def validate_retention(report_path: Path) -> pd.DataFrame:
    rows = []
    for coin, meta in COINS.items():
        checks = [
            path_status(f"{coin}_milestone1_daily_raw", ROOT / "milestone-1" / "daily" / f"{meta['m1']}_daily.csv"),
            path_status(f"{coin}_milestone1_hourly_raw", ROOT / "milestone-1" / "hourly" / f"{meta['m1']}_hourly.csv"),
            path_status(f"{coin}_live_daily", ROOT / "live_data" / "daily" / f"{meta['live']}_daily.csv"),
            path_status(f"{coin}_live_hourly", ROOT / "live_data" / "hourly" / f"{meta['live']}_hourly.csv"),
            path_status(f"{coin}_milestone2_daily_cleaned", ROOT / "milestone-2" / "infosys" / "cleaned data" / "daily" / meta["m2_daily"]),
            path_status(f"{coin}_milestone2_hourly_cleaned", ROOT / "milestone-2" / "infosys" / "cleaned data" / "hourly" / meta["m2_hourly"]),
            path_status(f"{coin}_daily_model", ROOT / "milestone-2" / "infosys" / "outputs" / "models" / "daily" / f"{meta.get('daily_model_alt', meta['model'])}.keras"),
            path_status(f"{coin}_hourly_model", ROOT / "milestone-2" / "infosys" / "outputs" / "models" / "hourly" / f"{meta['model']}.keras"),
            path_status(f"{coin}_daily_scaler", ROOT / "milestone-2" / "infosys" / "outputs" / "scalers" / "daily" / f"{meta.get('daily_model_alt', meta['model'])}.joblib"),
            path_status(f"{coin}_hourly_scaler", ROOT / "milestone-2" / "infosys" / "outputs" / "scalers" / "hourly" / f"{meta['model']}.joblib"),
        ]
        for check in checks:
            check["coin"] = coin
            rows.append(check)

    report = pd.DataFrame(rows)[["coin", "label", "path", "exists", "size_mb"]]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report.to_csv(report_path, index=False)
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate that all required coins, datasets, and artifacts are retained.")
    parser.add_argument("--report", default=str(REPORT_PATH))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = validate_retention(Path(args.report))
    missing = report[~report["exists"]]
    print(f"Retention checks written to {args.report}")
    if not missing.empty:
        print(missing[["coin", "label", "path"]].to_string(index=False))
        raise SystemExit(1)
    print(f"All retention checks passed for {len(COINS)} coins.")


if __name__ == "__main__":
    main()
