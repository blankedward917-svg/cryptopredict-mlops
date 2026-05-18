# Fresh Upload With DVC

The old `.git` directory was removed so this folder can become a fresh repository. The application does not need the old Git history to run.

## Recommended Upload Strategy

Use GitHub for code/configuration and DVC for datasets, models, scalers, and generated outputs.

Do not directly commit these heavy or generated paths to GitHub:

- `milestone-1`
- `milestone-2/infosys/cleaned data`
- `milestone-2/infosys/outputs`
- `live_data`
- `mlruns`
- `*.db`
- `*.csv`
- `*.keras`
- `*.joblib`

They are retained locally and should be stored through DVC remote storage.

## Fresh Git Repository

Run these only when you are ready to create the new repository:

```powershell
git init
git add .gitignore .gitattributes .dvcignore dvc.yaml params.yaml README.md docs scripts backened frontened prometheus grafana k8s argocd .github docker-compose.yml promptfooconfig.yaml prompts
git commit -m "Initial clean MLOps implementation"
```

## DVC Remote

For a local demo remote on E drive:

```powershell
dvc remote add -d localremote E:\mlops-dvc-storage
```

For cloud storage, replace the remote path with S3, GCS, Azure Blob, or another supported DVC remote.

## DVC Data Tracking

Run these when you are ready to version the full retained dataset and artifacts:

```powershell
dvc add milestone-1
dvc add "milestone-2/infosys/cleaned data"
dvc add "milestone-2/infosys/outputs"
dvc add live_data
dvc add backened/crypto_pro.db mlflow.db
dvc push
```

Then commit the generated `.dvc` pointer files and `.dvc/config`, not the heavy files themselves:

```powershell
git add .dvc .dvcignore *.dvc
git commit -m "Track datasets and model artifacts with DVC"
```

## Verification Commands

```powershell
python scripts/dataset_inventory.py
python scripts/validate_retention.py
python scripts/data_quality.py
python scripts/drift_monitor.py
dvc repro inventory --dry
```
