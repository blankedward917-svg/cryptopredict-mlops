# Clean MLOps Implementation Plan

This project should continue as the assignment project. It already contains the full product surface: crypto OHLCV datasets, LSTM training, model artifacts, a Flask/FastAPI serving layer, a React dashboard, and MLOps infrastructure.

The clean implementation keeps every coin and every dataset, but separates what each directory means.

## Dataset Contract

- `milestone-1/daily` and `milestone-1/hourly`: raw/raw-ish historical OHLCV files. These are the source history and should be treated as immutable input data.
- `milestone-2/infosys/cleaned data/daily` and `milestone-2/infosys/cleaned data/hourly`: cleaned, model-ready OHLCV files. These are the canonical training datasets.
- `live_data/daily` and `live_data/hourly`: live/synced working copies used by monitoring, validation, and demo refresh flows.
- `milestone-2/infosys/outputs`: trained models, scalers, prediction outputs, and metrics for all coins.

Generate the current inventory with:

```powershell
python scripts/dataset_inventory.py
```

Outputs are written to `reports/inventory/`.

## Tool Mapping

| Requirement | Project implementation |
| --- | --- |
| OpenLineage + Marquez | `backened/pipeline_runner.py` emits lineage events for sync, cleaning, and training with input/output dataset paths; Marquez runs from `docker-compose.yml`. |
| DVC | `dvc.yaml` defines validation, Feast, drift, and training stages. `.dvc/config` keeps the DVC remote and site cache under `.dvc/` so storage stays on the E drive. |
| Great Expectations | `scripts/data_quality.py` validates OHLCV columns, nulls, positive prices, and timestamp uniqueness. |
| Feast | `feature_repo/feature_store.yaml`, `feature_repo/feature_store_def.py`, `scripts/prepare_feast_source.py`, and `scripts/materialize_features.py` prepare, apply, and materialize the feature store. |
| MLflow | `backened/train_models.py` logs params, metrics, Keras models, and registered model names. Local artifacts are in `mlruns/` and `mlflow.db`. |
| Docker + Kubernetes | Backend/frontend Dockerfiles, `docker-compose.yml`, namespace, backend deployment, and frontend deployment manifests. |
| FastAPI + React | `backened/main.py` wraps the Flask app with FastAPI; React app lives in `frontened/cryptopredictpro`. |
| Evidently | `scripts/drift_monitor.py` generates the drift report. |
| Grafana + Prometheus | `prometheus/prometheus.yml`, Grafana datasource provisioning, and a provisioned overview dashboard. |
| GitHub + GitHub Actions | `.github/workflows/mlops-ci.yml` validates data quality, Feast, Evidently, Promptfoo, syntax, and Docker builds. |
| ArgoCD | `argocd/application.yaml`. |
| Promptfoo | `promptfooconfig.yaml` and `prompts/crypto_summary.txt`. |

## Recommended Demo Flow

1. Generate inventory: `python scripts/dataset_inventory.py`.
2. Run data quality checks on cleaned training data: `python scripts/data_quality.py`.
3. Prepare, apply, and materialize features: `dvc repro feast_source feast_apply feast_materialize`.
4. Run a short training job for demonstration: `python backened/train_models.py --freq hourly --epochs 1 --coins BTC,ETH,SOL`.
5. Start the stack: `docker compose up backend frontend prometheus grafana marquez-api marquez-web`.
6. Show API docs/health, React dashboard, Prometheus targets, Grafana dashboard, MLflow runs, Marquez lineage, and Promptfoo tests.
7. Generate drift report: `python scripts/drift_monitor.py`.

## Space Management

Keep datasets and all coins. The cleanup script is conservative and supports dry runs. Do not remove anything unless you explicitly choose that option.

```powershell
powershell -ExecutionPolicy Bypass -File scripts/clean_workspace.ps1 -DryRun
```

This workspace has been re-initialized as a lightweight Git repository for the SCM requirement. Large datasets, model artifacts, reports, and local environments remain excluded from Git and should be managed through DVC.

Docker is the largest C-drive consumer. To inspect Docker disk usage without deleting anything:

```powershell
docker system df
```

Only prune Docker artifacts when you are sure they are unused. Avoid pruning Docker volumes unless you are sure they do not contain useful databases.
