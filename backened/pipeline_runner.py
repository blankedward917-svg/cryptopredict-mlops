import argparse
import uuid
from pathlib import Path

import pandas as pd

from data_sync import run_sync

# OpenLineage Integration
from openlineage.client import OpenLineageClient, set_producer
from openlineage.client.run import InputDataset, Job, OutputDataset, Run, RunEvent, RunState

BASE = Path(__file__).resolve().parents[1]

# Initialize OpenLineage Client
# In production, this would be set via environment variables
OL_URL = "http://localhost:5001"
client = OpenLineageClient(url=OL_URL)
set_producer("https://github.com/sree1hack/cryptopredictpro/pipeline_runner.py")
NAMESPACE = "crypto-forecasting-pipeline"
DATASET_NAMESPACE = f"file://{BASE.as_posix()}"


def lineage_dataset(path: Path, output: bool = False):
    dataset_cls = OutputDataset if output else InputDataset
    resolved = path.resolve()
    facets = {
        "storage": {
            "_producer": "https://github.com/OpenLineage/OpenLineage",
            "_schemaURL": "https://openlineage.io/spec/facets/1-0-0/StorageDatasetFacet.json",
            "storageLayer": "filesystem",
            "fileFormat": resolved.suffix.lstrip(".") or "directory",
        }
    }
    return dataset_cls(namespace=DATASET_NAMESPACE, name=str(resolved.relative_to(BASE)), facets=facets)


def lineage_csvs(folder: Path, output: bool = False):
    return [lineage_dataset(path, output=output) for path in sorted(folder.glob("*.csv"))]


def emit_lineage(job_name, run_id, state, inputs=None, outputs=None):
    try:
        event = RunEvent(
            eventType=state,
            eventTime=pd.Timestamp.now(tz='UTC').isoformat(),
            run=Run(runId=run_id),
            job=Job(namespace=NAMESPACE, name=job_name),
            inputs=inputs or [],
            outputs=outputs or [],
            producer="https://github.com/sree1hack/cryptopredictpro/pipeline_runner.py"
        )
        client.emit(event)
    except Exception as e:
        print(f"Failed to emit OpenLineage event: {e}")


M1_DAILY = BASE / "milestone-1" / "daily"
M1_HOURLY = BASE / "milestone-1" / "hourly"
M2_DAILY = BASE / "milestone-2" / "infosys" / "cleaned data" / "daily"
M2_HOURLY = BASE / "milestone-2" / "infosys" / "cleaned data" / "hourly"

COINS = {
    "btc": {
        "daily": "bitcoin_inr_daily.csv",
        "hourly": "bitcoin_inr_hourly.csv",
        "instrument": "BTC-USD",
        "name": "Bitcoin",
    },
    "eth": {
        "daily": "ethereum_inr_daily.csv",
        "hourly": "ethereum_inr_hourly.csv",
        "instrument": "ETH-USD",
        "name": "Ethereum",
    },
    "doge": {
        "daily": "dogecoin_inr_daily.csv",
        "hourly": "dogecoin_inr_hourly.csv",
        "instrument": "DOGE-USD",
        "name": "Dogecoin",
    },
    "ltc": {
        "daily": "litecoin_inr_daily.csv",
        "hourly": "litecoin_inr_hourly.csv",
        "instrument": "LTC-USD",
        "name": "Litecoin",
    },
    "dot": {
        "daily": "polkadot_inr_daily.csv",
        "hourly": "polkadot_inr_hourly.csv",
        "instrument": "DOT-USD",
        "name": "Polkadot",
    },
    "polygon": {
        "daily": "polygon_inr_daily.csv",
        "hourly": "polygon_inr_hourly.csv",
        "instrument": "MATIC-USD",
        "name": "Polygon",
    },
    "ripple": {
        "daily": "ripple_inr_daily.csv",
        "hourly": "ripple_inr_hourly.csv",
        "instrument": "XRP-USD",
        "name": "Ripple",
    },
    "link": {
        "daily": "chainlink_coin_inr_daily.csv",
        "hourly": "chainlink_inr_hourly.csv",
        "instrument": "LINK-USD",
        "name": "Chainlink",
    },
    "bch": {
        "daily": "bitcoin_cash_inr_daily.csv",
        "hourly": "bitcoin_cash_inr_hourly.csv",
        "instrument": "BCH-USD",
        "name": "Bitcoin Cash",
    },
    "bnb": {
        "daily": "binance_coin_inr_daily.csv",
        "hourly": "binance_inr_hourly.csv",
        "instrument": "BNB-USD",
        "name": "Binance",
    },
    "ada": {
        "daily": "cardano_inr_daily.csv",
        "hourly": "cardano_inr_hourly.csv",
        "instrument": "ADA-USD",
        "name": "Cardano",
    },
    "avax": {
        "daily": "avalanche_inr_daily.csv",
        "hourly": "avalanche_inr_hourly.csv",
        "instrument": "AVAX-USD",
        "name": "Avalanche",
    },
    "sol": {
        "daily": "solana_inr_daily.csv",
        "hourly": "solana_inr_hourly.csv",
        "instrument": "SOL-USD",
        "name": "Solana",
    },
}


def clean_source(df: pd.DataFrame) -> pd.DataFrame:
    for col in ["OPEN", "HIGH", "LOW", "CLOSE"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["TIMESTAMP"] = pd.to_numeric(df["TIMESTAMP"], errors="coerce")
    df = df.dropna(subset=["TIMESTAMP", "OPEN", "HIGH", "LOW", "CLOSE"])
    df["TIMESTAMP"] = df["TIMESTAMP"].astype("int64")
    df = df[(df[["OPEN", "HIGH", "LOW", "CLOSE"]] >= 1).all(axis=1)]
    df = df.drop_duplicates(subset=["TIMESTAMP"], keep="last")
    return df.sort_values("TIMESTAMP").reset_index(drop=True)


def write_cleaned_milestone2() -> None:
    daily_merged = []
    hourly_merged = []

    for short_name, meta in COINS.items():
        source_daily = M1_DAILY / f"{short_name}_inr_daily.csv"
        source_hourly = M1_HOURLY / f"{short_name}_inr_hourly.csv"

        if not source_daily.exists() or not source_hourly.exists():
            print(f"Skipping {short_name}: source file missing")
            continue

        daily_df = clean_source(pd.read_csv(source_daily))
        daily_df["INSTRUMENT"] = meta["instrument"]
        daily_df["VOLUME"] = 1.0
        daily_df["DATE"] = pd.to_datetime(daily_df["TIMESTAMP"], unit="s", utc=True).dt.strftime(
            "%Y-%m-%d"
        )
        daily_out = daily_df[
            ["TIMESTAMP", "INSTRUMENT", "OPEN", "HIGH", "LOW", "CLOSE", "VOLUME", "DATE"]
        ]
        daily_out.to_csv(M2_DAILY / meta["daily"], index=False)

        daily_m = daily_out.copy()
        daily_m["Cryptocurrency"] = meta["name"]
        daily_merged.append(daily_m)

        hourly_df = clean_source(pd.read_csv(source_hourly))
        hourly_df["INSTRUMENT"] = meta["instrument"]
        hourly_df["VOLUME"] = 1.0
        dt_utc = pd.to_datetime(hourly_df["TIMESTAMP"], unit="s", utc=True)
        hourly_df["DATE_UTC"] = dt_utc.astype(str)
        hourly_df["DATE_IST"] = dt_utc.dt.tz_convert("Asia/Kolkata").astype(str)
        hourly_out = hourly_df[
            [
                "TIMESTAMP",
                "INSTRUMENT",
                "OPEN",
                "HIGH",
                "LOW",
                "CLOSE",
                "VOLUME",
                "DATE_UTC",
                "DATE_IST",
            ]
        ]
        hourly_out.to_csv(M2_HOURLY / meta["hourly"], index=False)

        hourly_m = hourly_out.copy()
        hourly_m["Cryptocurrency"] = meta["name"]
        hourly_merged.append(hourly_m)

    if daily_merged:
        pd.concat(daily_merged, ignore_index=True).sort_values(
            ["TIMESTAMP", "Cryptocurrency"]
        ).to_csv(M2_DAILY / "all_crypto_inr_daily_merged.csv", index=False)

    if hourly_merged:
        pd.concat(hourly_merged, ignore_index=True).sort_values(
            ["TIMESTAMP", "Cryptocurrency"]
        ).to_csv(M2_HOURLY / "all_crypto_inr_hourly_merged.csv", index=False)

    print("Milestone-2 cleaned files refreshed from milestone-1 sync data.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run sync, prepare milestone-2 cleaned files, and retrain models."
    )
    parser.add_argument("--skip-sync", action="store_true", help="Skip Coindesk sync step.")
    parser.add_argument("--prepare-only", action="store_true", help="Only refresh cleaned files.")
    parser.add_argument("--skip-train", action="store_true", help="Skip model training step.")
    parser.add_argument(
        "--freq",
        choices=["daily", "hourly", "both"],
        default="both",
        help="Training frequency when training is enabled.",
    )
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=64)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    pipeline_run_id = str(uuid.uuid4())

    if not args.skip_sync:
        print("Starting sync...")
        sync_run_id = str(uuid.uuid4())
        sync_outputs = lineage_csvs(M1_DAILY, output=True) + lineage_csvs(M1_HOURLY, output=True)
        emit_lineage("data_sync", sync_run_id, RunState.START, outputs=sync_outputs)
        run_sync()
        sync_outputs = lineage_csvs(M1_DAILY, output=True) + lineage_csvs(M1_HOURLY, output=True)
        emit_lineage("data_sync", sync_run_id, RunState.COMPLETE, outputs=sync_outputs)

    print("Refreshing Milestone-2 cleaned files...")
    clean_run_id = str(uuid.uuid4())
    clean_inputs = lineage_csvs(M1_DAILY) + lineage_csvs(M1_HOURLY)
    clean_outputs = lineage_csvs(M2_DAILY, output=True) + lineage_csvs(M2_HOURLY, output=True)
    emit_lineage("prepare_milestone2", clean_run_id, RunState.START, inputs=clean_inputs, outputs=clean_outputs)
    write_cleaned_milestone2()
    clean_outputs = lineage_csvs(M2_DAILY, output=True) + lineage_csvs(M2_HOURLY, output=True)
    emit_lineage("prepare_milestone2", clean_run_id, RunState.COMPLETE, inputs=clean_inputs, outputs=clean_outputs)

    if args.prepare_only or args.skip_train:
        print("Pipeline completed without training.")
        return

    from train_models import run_training

    print("Starting model training...")
    train_run_id = str(uuid.uuid4())
    train_inputs = lineage_csvs(M2_DAILY) + lineage_csvs(M2_HOURLY)
    train_outputs = [
        lineage_dataset(BASE / "milestone-2" / "infosys" / "outputs" / "models", output=True),
        lineage_dataset(BASE / "milestone-2" / "infosys" / "outputs" / "scalers", output=True),
        lineage_dataset(BASE / "milestone-2" / "infosys" / "outputs" / "predictions", output=True),
        lineage_dataset(BASE / "milestone-2" / "infosys" / "outputs" / "metrics", output=True),
    ]
    emit_lineage("train_models", train_run_id, RunState.START, inputs=train_inputs, outputs=train_outputs)
    run_training(freq=args.freq, epochs=args.epochs, batch_size=args.batch_size)
    emit_lineage("train_models", train_run_id, RunState.COMPLETE, inputs=train_inputs, outputs=train_outputs)


if __name__ == "__main__":
    main()
