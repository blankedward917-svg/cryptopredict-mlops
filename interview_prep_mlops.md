# MLOps Implementation Guide & Interview Prep

This document tracks the phased implementation of the MLOps pipeline for the Cryptocurrency Price Forecasting Platform. You can use these notes to defend your architectural decisions during your interview.

## Phase 1: Containerization & Modernization

### 1. Refactoring to FastAPI (Incremental Migration)
**What we did:**
Instead of rewriting all 800+ lines of your existing Flask `app.py` and potentially breaking your authentication and trading logic, we used a Senior Engineering pattern called the **Strangler Fig Pattern**. 
We created a new `main.py` using **FastAPI** and mounted your existing Flask app inside it using `WSGIMiddleware`.

**Why it matters for the interview:**
*   **Zero Downtime Migration:** You can tell the interviewer, "I wanted the performance and auto-generated Swagger UI of FastAPI, but didn't want to risk breaking the existing production Flask logic. So, I mounted Flask inside FastAPI. All new ML endpoints will be written purely in async FastAPI, while legacy routes remain in Flask until they are slowly deprecated."
*   **Modern Standards:** FastAPI is the industry standard for ML model serving because it handles high concurrency out-of-the-box using ASGI, unlike Flask which uses WSGI.

### 2. Dockerizing the Services
**What we did:**
We created a `Dockerfile` for both the React frontend and the FastAPI backend, and linked them using `docker-compose.yml`.

**Why it matters for the interview:**
*   **Reproducibility:** "It works on my machine" is not an MLOps answer. By containerizing, we ensure the code runs identically in development, staging, and production.
*   **Prerequisite for Kubernetes:** The orchestration step you requested (Kubernetes) strictly requires container images. This is the foundational layer.

---

## Phase 2: Core MLOps (Versioning & Tracking)

### 1. Experiment Tracking with MLflow
**What we did:**
We integrated `mlflow` into your `train_models.py` script. By wrapping the training process in `with mlflow.start_run()`, we now automatically log:
- **Parameters:** epochs, batch_size, window size, and horizon.
- **Metrics:** RMSE, MAE, and MAPE on both validation and test datasets.
- **Artifacts:** The final `.keras` model is saved directly to the MLflow registry.

**Why it matters for the interview:**
*   **Reproducibility & Comparison:** Without MLflow, if a model trains faster or has higher accuracy, you don't know *why*. Now, you can look at the MLflow dashboard and immediately compare Hyperparameters (like `window=60` vs `window=90`) and see how they affect the `test_MAPE`.
*   **Model Registry:** Instead of passing around `.keras` files locally, the MLflow model registry stores them centrally so CD pipelines can pull the "Staging" or "Production" tagged model.

### 2. Data Version Control (DVC)
**What we did:**
Added `dvc` to your requirements. In practice, you will run `dvc init` and track your `.csv` files using `dvc add milestone-2/infosys/cleaned data/`. DVC generates `.dvc` files that you commit to Git, while the actual heavy CSV files are stored in an S3 bucket or Google Cloud Storage.

**Why it matters for the interview:**
*   **Data Lineage tied to Code:** "Git is for code, DVC is for data." You can tell the interviewer that if you checkout a commit from 3 months ago, DVC will automatically pull the exact CSV dataset that was used to train the model in that specific commit.

---

## Phase 3: Data Quality & Feature Serving

### 1. Data Validation with Great Expectations
**What we did:**
We created `scripts/data_quality.py`. This script loads your incoming data into Great Expectations and asserts predefined rules (e.g., "Price must not be null," "Price must be strictly positive").

**Why it matters for the interview:**
*   **Preventing Silent Failures:** ML models don't crash when given bad data; they just silently make terrible predictions. Validating data *before* it hits the pipeline is a hallmark of a mature MLOps system.

### 2. Feature Management with Feast
**What we did:**
We created `scripts/feature_store_def.py` to define a Feast `FeatureView`. 

**Why it matters for the interview:**
*   **Training-Serving Skew:** Feast ensures that the exact same feature engineering logic used during model training is used during live inference in production. It acts as a bridge: retrieving batch data for training from the offline store, and syncing the latest values to an online store (like Redis) for lightning-fast API responses during your live predictions.

---

## Phase 4: Model Monitoring & Observability

### 1. Detecting Drift with Evidently AI
**What we did:**
We created `scripts/drift_monitor.py`. It compares your original training data against the live data you are fetching now. It automatically runs statistical tests (like the Kolmogorov-Smirnov test) to detect if the crypto market behavior has fundamentally shifted since you trained the LSTM.

**Why it matters for the interview:**
*   **Continuous Training (CT) Triggers:** "If Evidently detects data drift, I trigger an automated GitHub Action to retrain the model on the latest data." This answers the classic interview question: *How do you know when to retrain your model?*

### 2. OpenLineage & Marquez
**What we did:**
We integrated the `openlineage-python` client into `backened/pipeline_runner.py`. Every time the pipeline runs, it emits real-time metadata events to a **Marquez** server (running via Docker). 
- **Jobs Tracked:** `data_sync`, `prepare_milestone2`, and `train_models`.
- **Infrastructure:** Marquez UI is exposed at `http://localhost:3000` and the API at `http://localhost:5001`.

**Why it matters for the interview:**
*   **Operational Visibility:** "If a specific hourly CSV file gets corrupted, OpenLineage allows me to trace exactly which downstream models and predictions were affected. I don't have to guess; I have a visual dependency graph."
*   **Auditability:** In regulated industries, you must prove where your data came from. Marquez provides a versioned history of every data transformation and model training run.

---

## Phase 5: CI/CD & Production Infrastructure

### 1. Continuous Integration with GitHub Actions
**What we did:**
We created `.github/workflows/mlops-ci.yml`. Whenever you push code, this pipeline automatically runs your Python tests (`pytest`) AND your Great Expectations data quality checks, then builds a Docker container.

**Why it matters for the interview:**
*   **Automated Testing:** You demonstrate that code (and data assumptions) are tested automatically before anyone is allowed to merge to `main`. 

### 2. Continuous Deployment with Kubernetes & ArgoCD
**What we did:**
We implemented **GitOps** by creating an ArgoCD `Application` manifest in `argocd/application.yaml`. 
- **The Flow:** ArgoCD monitors your GitHub repository. When the CI pipeline updates the image tag in `k8s/backend-deployment.yaml`, ArgoCD detects the "Out of Sync" state and automatically applies the changes to the Kubernetes cluster.
- **Why it matters:** It eliminates manual deployments and ensures that the cluster state always matches the Git state (Single Source of Truth).

### 3. Prometheus & Grafana (Infrastructure Monitoring)
**What we did:**
We added Prometheus annotations to the Kubernetes pod (`prometheus.io/scrape: "true"`). 
**Why it matters:** While Evidently AI monitors the *Model's Brain* (Drift), Prometheus monitors the *Model's Body* (CPU usage, Memory, latency). If API latency spikes above 200ms, Grafana alerts the team.

### 4. Prompt Management (Promptfoo)
**What we did:**
We integrated **Promptfoo** for automated prompt testing. 
- **Configuration:** `promptfooconfig.yaml` defines tests for our LLM-based crypto summary feature.
- **Assertions:** We programmatically enforce that the LLM never gives financial advice and always includes a risk warning.
- **Why it matters:** Just like unit tests for code, we now have unit tests for our prompts to prevent hallucinations or compliance violations before they reach the user.
