from __future__ import annotations

from datetime import timedelta
from pathlib import Path

from feast import Entity, FeatureView, Field, FileSource, ValueType
from feast.types import Float32


ROOT = Path(__file__).resolve().parents[1]

crypto_instrument = Entity(
    name="crypto_instrument",
    join_keys=["INSTRUMENT"],
    value_type=ValueType.STRING,
    description="Cryptocurrency instrument such as BTC-USD or ETH-USD.",
)

crypto_hourly_source = FileSource(
    name="crypto_hourly_cleaned_source",
    path=str(ROOT / "reports" / "feast" / "crypto_hourly_features.parquet"),
    timestamp_field="DATE_UTC",
)

crypto_hourly_stats_view = FeatureView(
    name="crypto_hourly_stats",
    entities=[crypto_instrument],
    ttl=timedelta(days=7),
    schema=[
        Field(name="OPEN", dtype=Float32),
        Field(name="HIGH", dtype=Float32),
        Field(name="LOW", dtype=Float32),
        Field(name="CLOSE", dtype=Float32),
        Field(name="VOLUME", dtype=Float32),
    ],
    online=True,
    source=crypto_hourly_source,
    tags={"team": "mlops_assignment", "model": "lstm", "frequency": "hourly"},
)
