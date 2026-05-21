# CryptoPredictPro MLOps Toolchain: Interview & Live Demo Guide

This document is the **official reference and runbook** for demonstrating the MLOps toolchain of the **CryptoPredictPro** project during interviews and live demos. It details the **exact setup process followed in this repository**, where configurations are stored, the **installation commands**, and the **exact execution commands** to run in your terminal to showcase practical working.

---

## 🚀 Master Interview Demo Flow
If you have **10 minutes** to present the entire MLOps workflow to an interviewer, run these commands in this exact order:

1. **Dataset & Quality (DVC + Great Expectations)**:
   ```powershell
   python scripts/dataset_inventory.py
   python scripts/data_quality.py
   ```
2. **Feature Store (Feast)**:
   ```powershell
   dvc repro feast_source feast_apply feast_materialize
   ```
3. **Experiment Tracking (MLflow)**:
   ```powershell
   # Start the server (runs on port 5002, workers 1 bypasses Windows multiprocessing bug)
   mlflow ui --backend-store-uri sqlite:///mlflow.db --host 127.0.0.1 --port 5002 --workers 1
   # In another terminal, run a demo training run:
   python backened/train_models.py --freq hourly --epochs 1 --coins BTC,ETH,SOL
   ```
4. **Data Drift (Evidently AI)**:
   ```powershell
   python scripts/drift_monitor.py
   ```
5. **Prompt Evaluation (Promptfoo)**:
   ```powershell
   promptfoo eval -c promptfooconfig.yaml
   ```
6. **Full System Launch (Docker Compose + FastAPI + React + Prometheus + Grafana + Marquez)**:
   ```powershell
   docker compose up -d backend frontend prometheus grafana postgres marquez-api marquez-web
   ```
   * Show **React Frontend** at `http://localhost:8080`
   * Show **FastAPI Swagger Docs** at `http://localhost:5000/docs`
   * Show **Marquez Lineage Web UI** at `http://localhost:3000`
   * Show **Grafana Metrics Dashboard** at `http://localhost:3001`

---

## 🛠️ Step-by-Step Tool Reference (Setup, Installation & Demo Execution)

---

### 1. Data Lineage Tracking: OpenLineage + Marquez

#### A. How it is Setup in this Project
* **Lineage Provider**: Marquez API services are declared in [docker-compose.yml](file:///e:/ML-ops/docker-compose.yml) (`postgres`, `marquez-api`, `marquez-web`).
* **Lineage Emitter**: Emitted programmatically in [backened/pipeline_runner.py](file:///e:/ML-ops/backened/pipeline_runner.py) using the openlineage client. It sends pipeline metadata events for sync, cleaning, and training runs to the Marquez URL.

#### B. Installation Commands
```powershell
# Install OpenLineage Python packages
pip install openlineage-python openlineage-integration-common
```

#### C. Live Interview Demo Execution
```powershell
# 1. Start Marquez API, Marquez Web UI, and its Postgres metadata store
docker compose up -d postgres marquez-api marquez-web

# 2. Run the pipeline emulator to emit OpenLineage metadata events
python backened/pipeline_runner.py --skip-sync --prepare-only
```
* **What to Show the Interviewer**: 
  - Open `http://localhost:3000` in the browser.
  - Show the interactive graph showing the **Job** (`pipeline_runner`), the **input datasets** (raw datasets), and the **output datasets** (cleaned model datasets) with their exact schemas and run history.

#### D. Teardown
```powershell
docker compose stop postgres marquez-api marquez-web
```

---

### 2. Versioning: DVC (Data and Experiment Versioning)

#### A. How it is Setup in this Project
* **Configuration**: [.dvc/config](file:///e:/ML-ops/.dvc/config) is configured to use a local remote inside this workspace (`.dvc/local_remote`) and a site cache. This ensures heavy dataset files stay in the E-drive rather than consuming C-drive system space.
* **Pipeline Definitions**: [dvc.yaml](file:///e:/ML-ops/dvc.yaml) and [params.yaml](file:///e:/ML-ops/params.yaml) map dependencies, params, outputs, and metrics for the data quality, Feast, drift monitoring, and model training pipelines.

#### B. Installation Commands
```powershell
# Install DVC using pip
pip install dvc
```

#### C. Live Interview Demo Execution
```powershell
# 1. Inspect the defined pipeline stages without running them (Dry-run)
dvc repro inventory retention_check data_quality drift_report --dry

# 2. View the graphical representation of the MLOps pipeline stages in the terminal
dvc dag

# 3. Execute the demo model training pipeline stage using DVC
dvc repro train_demo_models
```
* **What to Show the Interviewer**:
  - Show how DVC tracks stages using `dvc.yaml` and caches massive outputs. Explain that large raw data and binary model weights are ignored by Git and managed by DVC.

#### D. Teardown
```powershell
# Clean DVC cache or dry runs if required (generally none needed)
```

---

### 3. Data Quality: Great Expectations

#### A. How it is Setup in this Project
* **Configuration**: Set up inside [scripts/data_quality.py](file:///e:/ML-ops/scripts/data_quality.py).
* **Validation Suite**: Implements validation logic directly on the 13 coins' cleaned daily and hourly datasets, validating schemas, non-null values, positive price values, and timestamp uniqueness.

#### B. Installation Commands
```powershell
# Install Great Expectations via pip
pip install great_expectations
```

#### C. Live Interview Demo Execution
```powershell
# Run the validation script in the terminal
python scripts/data_quality.py
```
* **What to Show the Interviewer**:
  - Explain that the script reads the cleaned hourly and daily datasets.
  - The terminal will print a structured validation log showing tests passed: "Schema check passed," "Null check passed," "Prices positive validation passed," "Timestamp uniqueness check passed."
  - Output report files are saved in `reports/data_quality_report.json`.

#### D. Teardown
```powershell
# No active background process
```

---

### 4. Feature Management: Feast (Feature Store)

#### A. How it is Setup in this Project
* **Repository Folder**: Located at [feature_repo/](file:///e:/ML-ops/feature_repo/).
* **Configs**: [feature_repo/feature_store.yaml](file:///e:/ML-ops/feature_repo/feature_store.yaml) defines a local provider with an SQLite registry and online database.
* **Definitions**: [feature_repo/feature_store_def.py](file:///e:/ML-ops/feature_repo/feature_store_def.py) defines the `crypto_instrument` entity, and the hourly features view (`crypto_hourly_stats`).
* **Scripts**: Ingestion source is prepared via `scripts/prepare_feast_source.py` and materialized using `scripts/materialize_features.py`.

#### B. Installation Commands
```powershell
# Install Feast feature store
pip install feast
```

#### C. Live Interview Demo Execution
```powershell
# 1. Execute Feast preparation, registry apply, and DB materialization via DVC
dvc repro feast_source feast_apply feast_materialize

# 2. Move to the repository and start the Feast Web Explorer UI
cd feature_repo
feast ui --port 8888
```
> [!IMPORTANT]
> **Windows Browser Routing Quirk**: Feast UI binds to the wildcard IP `0.0.0.0`. On Windows systems, modern browsers cannot resolve `0.0.0.0` directly, showing an `ERR_ADDRESS_INVALID` or `can't reach this page` error. You **MUST** type **`http://localhost:8888`** or **`http://127.0.0.1:8888`** in your browser's address bar to view the UI.

* **What to Show the Interviewer**:
  - Open `http://localhost:8888` in the browser (do not use `http://0.0.0.0:8888`).
  - Show the interactive Feature Store schema showing the **Entity** (`crypto_instrument`), the **Features View** (`crypto_hourly_stats`), and details of registered features.

#### D. Teardown
```powershell
# Exit feast ui (Ctrl+C) and return to workspace root
cd ..
```

---

### 5. Experiment Tracking: MLflow (Tracking & Registry)

#### A. How it is Setup in this Project
* **Server Backend**: Uses SQLite backend [mlflow.db](file:///e:/ML-ops/mlflow.db) for metadata and registers model runs to the [mlruns/](file:///e:/ML-ops/mlruns/) directory.
* **Integration**: Custom code inside [backened/train_models.py](file:///e:/ML-ops/backened/train_models.py) auto-logs model hyperparameters, Keras training loss metrics, scaler configs, and registers the output weights to the Model Registry (e.g. `crypto_hourly_bitcoin_inr`).

#### B. Installation Commands
```powershell
# Install MLflow tracking suite
pip install mlflow
```

#### C. Live Interview Demo Execution
```powershell
# 1. Start the MLflow central tracking server on port 5002 (workers 1 bypasses Windows multiprocessing bug)
mlflow ui --backend-store-uri sqlite:///mlflow.db --host 127.0.0.1 --port 5002 --workers 1

# 2. (In a separate terminal) Trigger a fast hourly model training demo for BTC, ETH, and SOL
python backened/train_models.py --freq hourly --epochs 1 --coins BTC,ETH,SOL
```
* **What to Show the Interviewer**:
  - Open `http://localhost:5002` in your browser.
  - Show the registered runs under the `crypto_forecasting` experiment.
  - Drill down into a run to show parameters (`epochs`, `lstm_units`, `coin`) and charts of loss metrics.
  - Show the **Models** tab where Keras models are saved and versioned inside the MLflow Model Registry.

#### D. Teardown
```powershell
# Stop the MLflow server (Ctrl+C in terminal window)
```

---

### 6. Orchestration: Docker + Kubernetes

#### A. How it is Setup in this Project
* **Docker Configurations**: Custom Dockerfiles in [backened/Dockerfile](file:///e:/ML-ops/backened/Dockerfile) and [frontened/cryptopredictpro/Dockerfile](file:///e:/ML-ops/frontened/cryptopredictpro/Dockerfile).
* **Multi-container Orchestration**: Configured in [docker-compose.yml](file:///e:/ML-ops/docker-compose.yml) to link backend, frontend, Prometheus, Grafana, and Marquez.
* **Kubernetes Manifests**: Located in [k8s/](file:///e:/ML-ops/k8s/) containing declarative pods, replica sets, and NodePort services.

#### B. Installation Commands
```powershell
# Install Docker Desktop and Minikube
winget install -e --id Docker.DockerDesktop
winget install -e --id Kubernetes.minikube
```

#### C. Live Interview Demo Execution
##### 1. Running Docker Compose Multi-Service Stack:
```powershell
# Build and run the entire ecosystem containerized in the background
docker compose up -d backend frontend prometheus grafana marquez-web

# List running containers
docker compose ps
```
##### 2. Running Kubernetes Cluster Deployments:
```powershell
# Start local minikube cluster
minikube start --driver=docker

# Apply manifests to spin up Kubernetes resources
kubectl apply -f k8s/

# Verify status of pods and services
kubectl get pods -o wide
kubectl get services
```

#### D. Teardown
```powershell
# Stop Docker containers
docker compose down

# Delete Kubernetes resources and stop Minikube
kubectl delete -f k8s/
minikube stop
```

---

### 7. Deployment: FastAPI (Serving) + ReactJS (Frontend)

#### A. How it is Setup in this Project
* **FastAPI Backend**: Wraps the prediction engines in [backened/main.py](file:///e:/ML-ops/backened/main.py) and [backened/app.py](file:///e:/ML-ops/backened/app.py), serving model predictions, authentication, and exposing a `/metrics` Prometheus endpoint.
* **ReactJS Dashboard**: Placed under [frontened/cryptopredictpro/](file:///e:/ML-ops/frontened/cryptopredictpro/). Shows the price predictions, trading simulator, authentication screens, and live tape tickers.

#### B. Installation Commands
```powershell
# Install Python server dependencies
pip install fastapi uvicorn gunicorn

# Install NodeJS frontend dependencies
cd frontened/cryptopredictpro
npm install
cd ../..
```

#### C. Live Interview Demo Execution
```powershell
# 1. Start FastAPI Serving layer
cd backened
uvicorn main:fastapi_app --host 127.0.0.1 --port 5000 --reload

# 2. (In a separate terminal) Start React Vite frontend
cd frontened/cryptopredictpro
npm run dev
```
* **What to Show the Interviewer**:
  - Open `http://localhost:5000/docs` in your browser to display the interactive Swagger documentation for FastAPI. Execute a `/predict` endpoint call.
  - Open `http://localhost:5173` (or port printed by Vite) to show the React UI login, predictive plots, and currency selections.

#### D. Teardown
```powershell
# Exit servers (Ctrl+C)
```

---

### 8. Monitoring: Evidently AI (Performance & Drift)

#### A. How it is Setup in this Project
* **Script**: Configured inside [scripts/drift_monitor.py](file:///e:/ML-ops/scripts/drift_monitor.py).
* **Logic**: Compares incoming live inference feature vectors in `live_data/` against target training distributions in `milestone-2/` and writes the outputs.

#### B. Installation Commands
```powershell
# Install Evidently AI monitoring package
pip install evidently
```

#### C. Live Interview Demo Execution
```powershell
# Run the drift analysis script
python scripts/drift_monitor.py
```
* **What to Show the Interviewer**:
  - The script will calculate data drift across hourly data features and export a file called `reports/drift/drift_report.html` (also placed at the root level).
  - Open `drift_report.html` in your browser to show the rich visualization of data distributions, target drift indices, and Kolmogorov-Smirnov statistical tests.

#### D. Teardown
```powershell
# No active background process
```

---

### 9. Infrastructure Monitoring: Grafana + Prometheus

#### A. How it is Setup in this Project
* **Prometheus configurations**: Managed in [prometheus/prometheus.yml](file:///e:/ML-ops/prometheus/prometheus.yml), configured to scrape endpoints including the FastAPI metric server.
* **Grafana configuration**: Provisioned using files in [grafana/](file:///e:/ML-ops/grafana/), containing a customized dashboard named **CryptoPredictPro MLOps Overview**.

#### B. Installation Commands
```powershell
# Deployed directly using Docker/Helm. Containers are configured in docker-compose.yml.
```

#### C. Live Interview Demo Execution
```powershell
# 1. Launch Prometheus & Grafana services in Docker Compose
docker compose up -d prometheus grafana
```
* **What to Show the Interviewer**:
  - Open Prometheus Targets: `http://localhost:9090` to prove that the `/metrics` endpoint is active and scraping.
  - Open Grafana: `http://localhost:3001` (Credentials: `admin` / `admin`).
  - Open **Dashboard -> CryptoPredictPro MLOps Overview** to show live system load, FastAPI throughput, and response latency.

#### D. Teardown
```powershell
docker compose stop prometheus grafana
```

---

### 10. SCM & CI: GitHub + GitHub Actions

#### A. How it is Setup in this Project
* **Repository**: Standardized as a Git project with ignored patterns mapped for safety.
* **CI Actions Workflow**: Declared inside [.github/workflows/mlops-ci.yml](file:///e:/ML-ops/.github/workflows/mlops-ci.yml). Runs code quality tests, executes Great Expectations assertions, verifies Feast configurations, runs Evidently validations, executes Promptfoo checks, and validates the Docker build on every pull request or push.

#### B. Installation Commands
```powershell
# Install Git and GitHub CLI
winget install -e --id Git.Git
winget install -e --id GitHub.cli
```

#### C. Live Interview Demo Execution
```powershell
# 1. Authenticate with GitHub (if not done already)
gh auth login

# 2. Check local status, commit, and push modifications to remote
git status
git add .
git commit -m "docs: improve live interview demo documentation in tools.md"
git push origin main

# 3. Trace CI runs in real-time in the terminal
gh run list
gh run watch
```
* **What to Show the Interviewer**:
  - Open the GitHub repository **Actions** tab.
  - Show the workflow executing the full suite of MLOps unit, validation, and build checks automatically.

#### D. Teardown
```powershell
# No active local process
```

---

### 11. Continuous Deployment: ArgoCD

#### A. How it is Setup in this Project
* **GitOps configuration**: Declared inside [argocd/application.yaml](file:///e:/ML-ops/argocd/application.yaml).
* **Logic**: Links the Kubernetes manifests directory `k8s/` to a target Kubernetes namespace and server, watching for updates.

#### B. Installation Commands
```powershell
# Install ArgoCD components inside Kubernetes cluster
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

#### C. Live Interview Demo Execution
```powershell
# 1. Deploy the declarative ArgoCD App integration manifest in Kubernetes
kubectl apply -f argocd/application.yaml

# 2. Expose the dashboard and open in browser
kubectl port-forward svc/argocd-server -n argocd 8080:443
```
* **What to Show the Interviewer**:
  - Access `https://localhost:8080` in the browser.
  - Show the application cluster graph showing target syncing between the GitHub state and your Kubernetes live resources.

#### D. Teardown
```powershell
kubectl delete -f argocd/application.yaml
```

---

### 12. Prompt Management: Promptfoo (Prompt Testing)

#### A. How it is Setup in this Project
* **Configuration**: Set up inside [promptfooconfig.yaml](file:///e:/ML-ops/promptfooconfig.yaml).
* **System Prompt**: Maintained inside [prompts/crypto_summary.txt](file:///e:/ML-ops/prompts/crypto_summary.txt).
* **Logic**: Performs automated semantic checks, assertions (e.g. confirming models include safety clauses, do not give financial advice, warn of risks), and tests multiple model configurations.

#### B. Installation Commands
```powershell
# Install promptfoo globally via npm
npm install -g promptfoo
```

#### C. Live Interview Demo Execution
```powershell
# 1. Execute the prompt evaluation suite defined in promptfooconfig.yaml
promptfoo eval -c promptfooconfig.yaml

# 2. Open the visual browser results dashboard
promptfoo view -p 15500
```
* **What to Show the Interviewer**:
  - Open `http://localhost:15500` in the browser.
  - Show the matrix of tests comparing model prompts, proving assertions (such as semantic bounds and safety checks) are fully verified and pass successfully.

#### D. Teardown
```powershell
# Stop promptfoo viewer (Ctrl+C in terminal)
```
