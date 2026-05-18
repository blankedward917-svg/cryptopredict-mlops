from __future__ import annotations

import argparse
from pathlib import Path

import great_expectations as gx
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = ROOT / "milestone-2" / "infosys" / "cleaned data"
DEFAULT_REPORT = ROOT / "reports" / "data_quality" / "results.csv"


def build_suite(context):
    suite = gx.ExpectationSuite(name="crypto_ohlcv_quality_suite")
    for column in ["TIMESTAMP", "INSTRUMENT", "OPEN", "HIGH", "LOW", "CLOSE"]:
        suite.add_expectation(gx.expectations.ExpectColumnToExist(column=column))
        suite.add_expectation(gx.expectations.ExpectColumnValuesToNotBeNull(column=column))

    for column in ["OPEN", "HIGH", "LOW", "CLOSE"]:
        suite.add_expectation(gx.expectations.ExpectColumnValuesToBeBetween(column=column, min_value=0.01))

    return suite


def validate_file(path: Path, context, suite) -> dict:
    batch = context.data_sources.pandas_default.read_csv(str(path))
    result = batch.validate(suite)

    df = pd.read_csv(path, usecols=lambda c: c in {"TIMESTAMP", "CLOSE", "INSTRUMENT"})
    timestamp_unique = True
    if "merged" not in path.name.lower() and "TIMESTAMP" in df.columns:
        timestamp_unique = not df["TIMESTAMP"].duplicated().any()

    close_has_values = "CLOSE" in df.columns and pd.to_numeric(df["CLOSE"], errors="coerce").notna().any()

    failed = [
        item.expectation_config.type
        for item in result.results
        if not item.success
    ]

    success = bool(result.success and timestamp_unique and close_has_values)
    return {
        "file": str(path.relative_to(ROOT)),
        "rows": len(df),
        "great_expectations_success": bool(result.success),
        "timestamp_unique": timestamp_unique,
        "close_has_values": close_has_values,
        "success": success,
        "failed_expectations": ";".join(failed),
    }


def validate_directory(data_dir: Path, report_path: Path) -> pd.DataFrame:
    context = gx.get_context(mode="ephemeral")
    suite = build_suite(context)
    files = sorted(data_dir.rglob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No CSV files found under {data_dir}")

    rows = [validate_file(path, context, suite) for path in files]
    results = pd.DataFrame(rows)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(report_path, index=False)
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Great Expectations checks on cleaned crypto datasets.")
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR))
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = validate_directory(Path(args.data_dir), Path(args.report))
    failures = results[~results["success"]]
    print(f"Validated {len(results)} CSV files. Report: {args.report}")
    if not failures.empty:
        print(failures[["file", "failed_expectations", "timestamp_unique", "close_has_values"]].to_string(index=False))
        raise SystemExit(1)
    print("All data quality checks passed.")


if __name__ == "__main__":
    main()
