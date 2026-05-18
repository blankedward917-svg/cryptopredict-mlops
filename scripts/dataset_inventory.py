from __future__ import annotations

import argparse
import sqlite3
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

DATASET_GROUPS = {
    "milestone_1_daily_raw": ROOT / "milestone-1" / "daily",
    "milestone_1_hourly_raw": ROOT / "milestone-1" / "hourly",
    "milestone_2_daily_cleaned": ROOT / "milestone-2" / "infosys" / "cleaned data" / "daily",
    "milestone_2_hourly_cleaned": ROOT / "milestone-2" / "infosys" / "cleaned data" / "hourly",
    "live_daily": ROOT / "live_data" / "daily",
    "live_hourly": ROOT / "live_data" / "hourly",
}

OUTPUT_GROUPS = {
    "models_daily": ROOT / "milestone-2" / "infosys" / "outputs" / "models" / "daily",
    "models_hourly": ROOT / "milestone-2" / "infosys" / "outputs" / "models" / "hourly",
    "scalers_daily": ROOT / "milestone-2" / "infosys" / "outputs" / "scalers" / "daily",
    "scalers_hourly": ROOT / "milestone-2" / "infosys" / "outputs" / "scalers" / "hourly",
    "predictions_daily": ROOT / "milestone-2" / "infosys" / "outputs" / "predictions" / "daily",
    "predictions_hourly": ROOT / "milestone-2" / "infosys" / "outputs" / "predictions" / "hourly",
    "metrics_daily": ROOT / "milestone-2" / "infosys" / "outputs" / "metrics" / "daily",
    "metrics_hourly": ROOT / "milestone-2" / "infosys" / "outputs" / "metrics" / "hourly",
}

DB_PATH = ROOT / "backened" / "crypto_pro.db"


@dataclass
class CsvProfile:
    group: str
    file: str
    rows: int
    columns: str
    min_time: str
    max_time: str
    span_days: float | None
    close_min: float | None
    close_max: float | None
    size_mb: float


def _read_header(path: Path) -> list[str]:
    return list(pd.read_csv(path, nrows=0).columns)


def _time_range(df: pd.DataFrame) -> tuple[str, str, float | None]:
    if "TIMESTAMP" in df.columns:
        ts = pd.to_numeric(df["TIMESTAMP"], errors="coerce").dropna()
        if not ts.empty:
            dt = pd.to_datetime(ts, unit="s", utc=True)
            return str(dt.min()), str(dt.max()), round((dt.max() - dt.min()).total_seconds() / 86400, 2)

    for col in ["DATE_UTC", "DATE", "date"]:
        if col in df.columns:
            dt = pd.to_datetime(df[col], errors="coerce", utc=True).dropna()
            if not dt.empty:
                return str(dt.min()), str(dt.max()), round((dt.max() - dt.min()).total_seconds() / 86400, 2)

    return "", "", None


def profile_csv(group: str, path: Path) -> CsvProfile:
    df = pd.read_csv(path)
    min_time, max_time, span_days = _time_range(df)

    close_col = "CLOSE" if "CLOSE" in df.columns else "close" if "close" in df.columns else None
    close_min = close_max = None
    if close_col:
        close = pd.to_numeric(df[close_col], errors="coerce").dropna()
        if not close.empty:
            close_min = float(close.min())
            close_max = float(close.max())

    return CsvProfile(
        group=group,
        file=str(path.relative_to(ROOT)),
        rows=len(df),
        columns=",".join(_read_header(path)),
        min_time=min_time,
        max_time=max_time,
        span_days=span_days,
        close_min=close_min,
        close_max=close_max,
        size_mb=round(path.stat().st_size / (1024 * 1024), 3),
    )


def collect_csv_profiles() -> pd.DataFrame:
    rows = []
    for group, folder in DATASET_GROUPS.items():
        if not folder.exists():
            continue
        for path in sorted(folder.glob("*.csv")):
            rows.append(profile_csv(group, path).__dict__)
    return pd.DataFrame(rows)


def collect_output_inventory() -> pd.DataFrame:
    rows = []
    for group, folder in OUTPUT_GROUPS.items():
        if not folder.exists():
            continue
        files = list(folder.glob("*"))
        rows.append(
            {
                "group": group,
                "path": str(folder.relative_to(ROOT)),
                "files": len([p for p in files if p.is_file()]),
                "size_mb": round(sum(p.stat().st_size for p in files if p.is_file()) / (1024 * 1024), 3),
            }
        )
    return pd.DataFrame(rows)


def collect_db_inventory() -> pd.DataFrame:
    if not DB_PATH.exists():
        return pd.DataFrame()

    conn = sqlite3.connect(DB_PATH)
    try:
        query = """
            SELECT coin, timeframe, COUNT(*) AS rows, MIN(timestamp) AS min_ts, MAX(timestamp) AS max_ts
            FROM ohlcv
            GROUP BY coin, timeframe
            ORDER BY coin, timeframe
        """
        df = pd.read_sql_query(query, conn)
    finally:
        conn.close()

    if df.empty:
        return df

    df["min_time"] = pd.to_datetime(df["min_ts"], unit="s", utc=True).astype(str)
    df["max_time"] = pd.to_datetime(df["max_ts"], unit="s", utc=True).astype(str)
    df["span_days"] = ((df["max_ts"] - df["min_ts"]) / 86400).round(2)
    return df[["coin", "timeframe", "rows", "min_time", "max_time", "span_days"]]


def write_report(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_profiles = collect_csv_profiles()
    output_inventory = collect_output_inventory()
    db_inventory = collect_db_inventory()

    csv_profiles.to_csv(output_dir / "dataset_inventory.csv", index=False)
    output_inventory.to_csv(output_dir / "artifact_inventory.csv", index=False)
    if not db_inventory.empty:
        db_inventory.to_csv(output_dir / "db_ohlcv_inventory.csv", index=False)

    summary_lines = [
        "# Dataset Inventory",
        "",
        "This report is generated by `python scripts/dataset_inventory.py`.",
        "",
        "## Dataset Groups",
    ]

    if not csv_profiles.empty:
        group_summary = (
            csv_profiles.groupby("group")
            .agg(files=("file", "count"), rows=("rows", "sum"), size_mb=("size_mb", "sum"))
            .reset_index()
        )
        for row in group_summary.itertuples(index=False):
            summary_lines.append(
                f"- `{row.group}`: {row.files} CSV files, {int(row.rows):,} rows, {row.size_mb:.2f} MB"
            )

    summary_lines.extend(["", "## Artifact Groups"])
    if not output_inventory.empty:
        for row in output_inventory.itertuples(index=False):
            summary_lines.append(f"- `{row.group}`: {row.files} files, {row.size_mb:.2f} MB")

    if not db_inventory.empty:
        summary_lines.extend(["", "## SQLite OHLCV Table"])
        for row in db_inventory.itertuples(index=False):
            summary_lines.append(
                f"- `{row.coin}` `{row.timeframe}`: {int(row.rows):,} rows, {row.min_time} to {row.max_time}"
            )

    summary_lines.extend(
        [
            "",
            "## Notes",
            "- `milestone-1` keeps raw/raw-ish historical OHLCV files.",
            "- `milestone-2/infosys/cleaned data` keeps model-ready cleaned files.",
            "- `live_data` keeps the latest synced working copy used by monitoring and prompt demos.",
            "- `milestone-2/infosys/outputs` keeps trained models, scalers, metrics, and prediction outputs.",
        ]
    )

    (output_dir / "dataset_inventory.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Profile all retained crypto datasets and model artifacts.")
    parser.add_argument("--output-dir", default=str(ROOT / "reports" / "inventory"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    write_report(output_dir)
    print(f"Inventory written to {output_dir}")


if __name__ == "__main__":
    main()
