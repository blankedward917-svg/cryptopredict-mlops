from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = (
    ROOT
    / "milestone-2"
    / "infosys"
    / "cleaned data"
    / "hourly"
    / "all_crypto_inr_hourly_merged.csv"
)
DEFAULT_OUTPUT = ROOT / "reports" / "feast" / "crypto_hourly_features.parquet"


def build_feature_source(input_path: Path, output_path: Path, rows_per_instrument: int) -> None:
    columns = ["INSTRUMENT", "DATE_UTC", "OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]
    df = pd.read_csv(input_path, usecols=columns)
    df["DATE_UTC"] = pd.to_datetime(df["DATE_UTC"], utc=True, errors="coerce")
    for column in ["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.dropna(subset=columns).sort_values(["INSTRUMENT", "DATE_UTC"])
    df = df.groupby("INSTRUMENT", group_keys=False).tail(rows_per_instrument)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)
    print(f"Wrote Feast parquet source: {output_path} ({len(df)} rows)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a compact parquet source for Feast.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--rows-per-instrument", type=int, default=500)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_feature_source(Path(args.input), Path(args.output), args.rows_per_instrument)


if __name__ == "__main__":
    main()
