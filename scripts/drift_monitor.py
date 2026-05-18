from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from evidently import Report
from evidently.presets import DataDriftPreset


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REFERENCE = ROOT / "milestone-2" / "infosys" / "cleaned data" / "hourly" / "bitcoin_inr_hourly.csv"
DEFAULT_CURRENT = ROOT / "live_data" / "hourly" / "btc_inr_hourly.csv"
DEFAULT_OUTPUT = ROOT / "reports" / "drift" / "drift_report.html"


def load_features(path: Path) -> pd.DataFrame:
    features = ["OPEN", "HIGH", "LOW", "CLOSE"]
    df = pd.read_csv(path)
    missing = [column for column in features if column not in df.columns]
    if missing:
        raise ValueError(f"{path} is missing required drift columns: {missing}")
    return df[features].apply(pd.to_numeric, errors="coerce").dropna()


def generate_drift_report(ref_data_path: Path, curr_data_path: Path, output_path: Path) -> None:
    print(f"Reference data: {ref_data_path}")
    print(f"Current data: {curr_data_path}")
    reference = load_features(ref_data_path)
    current = load_features(curr_data_path)

    report = Report(metrics=[DataDriftPreset()])
    snapshot = report.run(reference_data=reference, current_data=current)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot.save_html(str(output_path))
    print(f"Drift report generated at: {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate an Evidently data drift report.")
    parser.add_argument("--reference", default=str(DEFAULT_REFERENCE))
    parser.add_argument("--current", default=str(DEFAULT_CURRENT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generate_drift_report(Path(args.reference), Path(args.current), Path(args.output))


if __name__ == "__main__":
    main()
