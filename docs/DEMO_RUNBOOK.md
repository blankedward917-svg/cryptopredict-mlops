# Demo Runbook

This runbook shows the assignment end to end while keeping the full dataset and all coins retained. Use BTC/ETH/SOL only as a fast demo profile.

## 1. Prove Dataset Retention

```powershell
python scripts/dataset_inventory.py
python scripts/validate_retention.py
```

Show:

- `reports/inventory/dataset_inventory.md`
- `reports/inventory/retention_check.csv`

Expected result: all retention checks pass for 13 coins.

## 2. DVC Pipeline

This repo is configured to use a lightweight local DVC remote and site cache under `.dvc/`, which keeps DVC data inside this E-drive workspace instead of consuming C drive space.

Inspect non-training stages:

```powershell
dvc repro inventory retention_check data_quality drift_report --dry
```

Run the fast demo training stage:

```powershell
dvc repro train_demo_models
```

Run full training only when you want to refresh every retained model:

```powershell
dvc repro train_models
```

## 3. Great Expectations Data Quality

```powershell
python scripts/data_quality.py
```

Show:

- required OHLCV columns exist
- values are non-null
- prices are positive
- per-coin timestamps are unique

## 4. Feast Feature Store

Show:

- `feature_repo/feature_store_def.py`
- `feature_repo/feature_store.yaml`
- entity: `crypto_instrument`
- source: all-coin cleaned hourly CSV
- feature view: `crypto_hourly_stats`

Prepare the compact parquet source, apply the feature repository, and materialize the online store:

```powershell
dvc repro feast_source
dvc repro feast_apply
dvc repro feast_materialize
```

Show:

- `reports/feast/crypto_hourly_features.parquet`
- `reports/feast/registry.db`
- `reports/feast/online_store.db`

## 5. MLflow Tracking

Train demo models:

```powershell
python backened/train_models.py --freq hourly --epochs 1 --coins BTC,ETH,SOL
```

Open MLflow:

```powershell
mlflow ui --backend-store-uri sqlite:///mlflow.db --host 127.0.0.1 --port 5002
```

Show experiment `crypto_forecasting` with params and metrics.
Training also registers each model under names like `crypto_hourly_bitcoin_inr`.

## 6. FastAPI Serving

```powershell
cd backened
uvicorn main:fastapi_app --host 0.0.0.0 --port 5000
```

Show:

- `http://localhost:5000/fastapi-health`
- `http://localhost:5000/metrics`
- prediction POST `/predict`

## 7. React Dashboard

```powershell
cd frontened/cryptopredictpro
npm install
npm run dev
```

Show dashboard prediction flow and live coin tape.

## 8. Evidently Drift Report

```powershell
python scripts/drift_monitor.py
```

Show:

- `reports/drift/drift_report.html`

## 9. Prometheus and Grafana

```powershell
docker compose up prometheus grafana
```

Show:

- Prometheus targets at `http://localhost:9090`
- Grafana at `http://localhost:3001`
- provisioned dashboard: `CryptoPredictPro MLOps Overview`

## 10. OpenLineage and Marquez

```powershell
docker compose up postgres marquez-api marquez-web
python backened/pipeline_runner.py --skip-sync --prepare-only
```

Show:

- Marquez UI at `http://localhost:3000`
- pipeline jobs for sync, data prep, and training when enabled
- input and output dataset paths attached to lineage events

## 11. CI/CD and GitOps

Show:

- `.github/workflows/mlops-ci.yml`
- `k8s/backend-deployment.yaml`
- `k8s/frontend-deployment.yaml`
- `argocd/application.yaml`

Explain flow:

GitHub push -> DVC/GE/Feast/Evidently/Promptfoo checks -> backend and frontend Docker builds -> optional registry push when secrets are configured -> ArgoCD syncs Kubernetes manifests.

## 12. Promptfoo

```powershell
promptfoo eval -c promptfooconfig.yaml
```

Show assertions:

- summary includes risk warning
- summary states it is not financial advice
