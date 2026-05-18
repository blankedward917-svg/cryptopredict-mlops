from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sys

import pandas as pd
from feast import FeatureStore


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from feature_repo.feature_store_def import crypto_hourly_stats_view, crypto_instrument

REPO_PATH = ROOT / "feature_repo"
SOURCE_PATH = (
    ROOT
    / "reports"
    / "feast"
    / "crypto_hourly_features.parquet"
)


def event_time_window() -> tuple[datetime, datetime]:
    df = pd.read_parquet(SOURCE_PATH, columns=["DATE_UTC"])
    timestamps = pd.to_datetime(df["DATE_UTC"], utc=True, errors="coerce").dropna()
    if timestamps.empty:
        now = datetime.now(timezone.utc)
        return now, now
    return timestamps.min().to_pydatetime(), timestamps.max().to_pydatetime()


def main() -> None:
    store = FeatureStore(repo_path=str(REPO_PATH))
    store.apply([crypto_instrument, crypto_hourly_stats_view])
    start_date, end_date = event_time_window()
    store.materialize(start_date=start_date, end_date=end_date)
    print("Feast registry and online store refreshed under reports/feast.")


if __name__ == "__main__":
    main()
