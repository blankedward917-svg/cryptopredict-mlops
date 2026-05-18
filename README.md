# CryptoPredictPro MLOps Assignment

CryptoPredictPro is an end-to-end MLOps implementation for cryptocurrency price forecasting. It keeps the full multi-coin dataset and demonstrates data versioning, validation, feature management, experiment tracking, model serving, monitoring, CI/CD, and deployment infrastructure.

## What This Project Contains

- Full raw/raw-ish OHLCV history in `milestone-1`.
- Cleaned model-ready datasets in `milestone-2/infosys/cleaned data`.
- Trained Keras LSTM models, scalers, metrics, and prediction outputs in `milestone-2/infosys/outputs`.
- Live/synced working datasets in `live_data`.
- Flask prediction/trading/auth API wrapped by FastAPI for modern serving and Prometheus metrics.
- React/Vite frontend for login, prediction dashboard, live prices, and trading UI.
- MLOps integrations for DVC, Great Expectations, Feast, MLflow, Evidently, OpenLineage/Marquez, Docker, Kubernetes, Prometheus, Grafana, GitHub Actions, ArgoCD, and Promptfoo.

## Supported Coins

`BTC`, `ETH`, `DOGE`, `LTC`, `DOT`, `MATIC`, `XRP`, `LINK`, `BCH`, `BNB`, `SOL`, `ADA`, `AVAX`

## Important Docs

- [End-to-End Architecture](docs/END_TO_END_ARCHITECTURE.md)
- [Dataset Architecture](docs/DATASET_ARCHITECTURE.md)
- [Clean MLOps Implementation](docs/MLOPS_CLEAN_IMPLEMENTATION.md)
- [Demo Runbook](docs/DEMO_RUNBOOK.md)
- [Fresh Upload With DVC](docs/FRESH_UPLOAD_WITH_DVC.md)
- [Production Checklist](PRODUCTION_CHECKLIST.md)

## Quick Verification

```powershell
python scripts/dataset_inventory.py
python scripts/validate_retention.py
python scripts/data_quality.py
python scripts/drift_monitor.py
```

Generated reports are written under `reports/`.

## Backend

Install dependencies:

```powershell
pip install -r backened/requirements.txt
```

Run FastAPI wrapper:

```powershell
cd backened
uvicorn main:fastapi_app --host 0.0.0.0 --port 5000
```

Legacy Flask direct mode is also available:

```powershell
python backened/app.py
```

## Frontend

```powershell
cd frontened/cryptopredictpro
npm install
npm run dev
```

Set `VITE_API_URL` in `frontened/cryptopredictpro/.env` when the backend is not at the default local URL.

## Docker Demo

```powershell
docker compose up backend frontend prometheus grafana marquez-api marquez-web
```

Useful URLs:

- Frontend: `http://localhost:8080`
- Backend/FastAPI: `http://localhost:5000/fastapi-health`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3001`
- Marquez UI: `http://localhost:3000`

## DVC Pipeline

The project includes `dvc.yaml` and `params.yaml`.

```powershell
dvc repro inventory
dvc repro data_quality
dvc repro feast_source
dvc repro feast_apply
dvc repro feast_materialize
dvc repro retention_check
dvc repro drift_report
```

DVC is configured with a local remote and site cache under `.dvc/`, so DVC data stays inside this E-drive workspace instead of using C drive space.

Fast demo training profile:

```powershell
python backened/train_models.py --freq hourly --epochs 1 --coins BTC,ETH,SOL
```

Full retained model training:

```powershell
python backened/train_models.py --freq both --epochs 3 --coins all
```

Use DVC remote storage for heavy datasets and model artifacts before uploading the fresh repository to GitHub. See [Fresh Upload With DVC](docs/FRESH_UPLOAD_WITH_DVC.md).
