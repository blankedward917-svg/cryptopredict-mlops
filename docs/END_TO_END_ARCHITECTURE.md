# End-to-End MLOps Architecture

This project is organized as a full MLOps system. The retained system of record includes all 13 supported coins, while the recommended live demo profile uses BTC, ETH, and SOL to keep walkthroughs fast.

## High-Level Flow

```mermaid
flowchart LR
    A[Milestone-1 raw OHLCV] --> B[Cleaning and merge scripts]
    B --> C[Milestone-2 cleaned OHLCV]
    C --> D[Great Expectations validation]
    C --> E[Feast registry and online store]
    C --> F[LSTM training]
    F --> G[MLflow tracking and registry]
    F --> H[Keras models and scalers]
    H --> I[FastAPI plus Flask serving API]
    I --> J[React dashboard]
    I --> K[Prometheus metrics]
    K --> L[Grafana dashboard]
    C --> M[Evidently drift report]
    N[Pipeline runner] --> O[OpenLineage events]
    O --> P[Marquez lineage UI]
    Q[GitHub Actions] --> R[Validation and Docker build]
    R --> S[Kubernetes manifests]
    S --> T[ArgoCD GitOps deployment]
    U[Prompt templates] --> V[Promptfoo tests]
```

## Data Layers

The data layers are intentionally separate:

- **Raw layer:** `milestone-1/daily`, `milestone-1/hourly`
- **Clean training layer:** `milestone-2/infosys/cleaned data/daily`, `milestone-2/infosys/cleaned data/hourly`
- **Live/monitoring layer:** `live_data/daily`, `live_data/hourly`
- **Serving DB layer:** `backened/crypto_pro.db`, table `ohlcv`
- **Model artifact layer:** `milestone-2/infosys/outputs`

All coins are retained. BTC/ETH/SOL is only a fast demo profile.

## Assignment Tool Coverage

| Area | Tool | Implementation |
| --- | --- | --- |
| Data lineage | OpenLineage + Marquez | `backened/pipeline_runner.py` emits sync, cleaning, and training events with input/output dataset paths. Marquez services run in `docker-compose.yml`. |
| Versioning | DVC | `dvc.yaml`, `params.yaml`, `.dvcignore`, and `.dvc/config` define reproducible inventory, validation, Feast, drift, and training stages with local E-drive-friendly DVC storage under `.dvc/`. |
| Data quality | Great Expectations | `scripts/data_quality.py` checks cleaned OHLCV files for required columns, non-null values, positive prices, and timestamp uniqueness. |
| Feature management | Feast | `feature_repo/feature_store.yaml`, `feature_repo/feature_store_def.py`, `scripts/prepare_feast_source.py`, and `scripts/materialize_features.py` prepare, apply, and materialize the crypto feature store. |
| Experiment tracking | MLflow | `backened/train_models.py` logs params, RMSE/MAE/MAPE metrics, Keras models, and registered model names. |
| Serving | FastAPI | `backened/main.py` wraps the existing Flask app and exposes metrics. |
| Frontend | ReactJS | `frontened/cryptopredictpro` contains the prediction and trading dashboard. |
| Model/data monitoring | Evidently AI | `scripts/drift_monitor.py` creates an HTML drift report. |
| Infra monitoring | Prometheus + Grafana | `prometheus/prometheus.yml`, Grafana datasource provisioning, and a provisioned overview dashboard. |
| CI | GitHub Actions | `.github/workflows/mlops-ci.yml` runs DVC restore, data quality, syntax checks, Feast checks, Evidently smoke test, Promptfoo tests, and Docker builds. |
| CD | ArgoCD | `argocd/application.yaml` deploys Kubernetes manifests from `k8s/`. |
| Orchestration/deployment | Docker + Kubernetes | `docker-compose.yml`, backend/frontend Dockerfiles, backend/frontend Kubernetes deployments, and namespace manifest. |
| Prompt management | Promptfoo | `promptfooconfig.yaml`, `prompts/crypto_summary.txt`. |

## Demo Profile

For a fast evaluator demo, run the whole stack against:

`BTC,ETH,SOL`

The training script supports this with:

```powershell
python backened/train_models.py --freq hourly --epochs 1 --coins BTC,ETH,SOL
```

The full retained training set remains available with:

```powershell
python backened/train_models.py --freq both --epochs 3 --coins all
```

## Runtime Architecture

```mermaid
flowchart TB
    subgraph Data
        D1[Cleaned CSVs]
        D2[SQLite/Postgres OHLCV]
        D3[Keras models]
        D4[Scalers]
    end

    subgraph Backend
        B1[FastAPI wrapper]
        B2[Mounted Flask routes]
        B3[Prediction endpoint]
        B4[Auth and trading endpoints]
        B5[Prometheus /metrics]
    end

    subgraph Frontend
        F1[React dashboard]
        F2[Prediction charts]
        F3[Live coin tape]
        F4[Trading panel]
    end

    D1 --> B3
    D2 --> B3
    D3 --> B3
    D4 --> B3
    B1 --> B2
    B2 --> B3
    B2 --> B4
    B1 --> B5
    F1 --> B3
    F1 --> B4
    F1 --> F2
    F1 --> F3
    F1 --> F4
```
