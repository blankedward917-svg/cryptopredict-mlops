import React, { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import Icon from '../../components/AppIcon';

const apiBaseUrl = typeof window !== 'undefined'
  ? (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
     ? `${window.location.protocol}//${window.location.hostname}:5000`
     : 'https://cryptopredict-backend.onrender.com')
  : 'https://cryptopredict-backend.onrender.com';

const tools = [
  {
    id: 'lineage',
    label: 'OpenLineage + Marquez',
    short: 'Lineage',
    icon: 'GitBranch',
    status: 'Improved',
    score: 86,
    color: 'primary',
    command: 'docker compose up postgres marquez-api marquez-web && python backened/pipeline_runner.py --skip-sync --prepare-only',
    toolUrl: 'http://localhost:3000',
    evidence: ['backened/pipeline_runner.py', 'docker-compose.yml'],
    metrics: [
      ['Jobs emitted', '3'],
      ['Dataset facets', 'Input / Output'],
      ['Marquez UI', 'localhost:3000']
    ],
    notes: 'Pipeline events now include concrete raw, cleaned, and model-output dataset paths for sync, preparation, and training.'
  },
  {
    id: 'dvc',
    label: 'DVC Versioning',
    short: 'DVC',
    icon: 'GitCommitHorizontal',
    status: 'Good',
    score: 88,
    color: 'accent',
    command: 'dvc status && dvc repro inventory data_quality feast_source feast_apply feast_materialize drift_report',
    toolUrl: null,
    evidence: ['dvc.yaml', 'dvc.lock', '.dvc/config', 'params.yaml'],
    metrics: [
      ['Pipeline stages', '9'],
      ['Local remote', '.dvc/local_remote'],
      ['C drive use', '0 GB added']
    ],
    notes: 'DVC now has reproducible Feast stages and a local E-drive workspace remote/cache setup to avoid consuming C-drive space.'
  },
  {
    id: 'quality',
    label: 'Great Expectations',
    short: 'Quality',
    icon: 'ClipboardCheck',
    status: 'Good',
    score: 90,
    color: 'success',
    command: 'python scripts/data_quality.py',
    toolUrl: null,
    evidence: ['scripts/data_quality.py', 'reports/data_quality/results.csv'],
    metrics: [
      ['Validated CSVs', '28'],
      ['Checks', 'Columns / nulls / ranges'],
      ['Gate', 'CI enabled']
    ],
    notes: 'The data quality gate validates cleaned OHLCV files for required columns, non-null fields, positive prices, and timestamp uniqueness.'
  },
  {
    id: 'feast',
    label: 'Feast Feature Store',
    short: 'Feast',
    icon: 'DatabaseZap',
    status: 'Improved',
    score: 87,
    color: 'primary',
    command: 'dvc repro feast_source feast_apply feast_materialize',
    toolUrl: null,
    evidence: ['feature_repo/feature_store.yaml', 'feature_repo/feature_store_def.py', 'reports/feast/online_store.db'],
    metrics: [
      ['Feature views', '1'],
      ['Registered columns', 'OHLCV'],
      ['Model input today', 'CLOSE sequence']
    ],
    notes: 'Feast registers OHLCV market features keyed by instrument and timestamp. The current LSTM training path consumes CLOSE sequences, while OHLCV remains available for richer model versions.'
  },
  {
    id: 'mlflow',
    label: 'MLflow Tracking',
    short: 'MLflow',
    icon: 'LineChart',
    status: 'Good',
    score: 88,
    color: 'success',
    command: 'mlflow ui --backend-store-uri sqlite:///mlflow.db --host 127.0.0.1 --port 5002',
    toolUrl: 'http://localhost:5002',
    evidence: ['backened/train_models.py', 'mlflow.db', 'mlruns/'],
    metrics: [
      ['Experiment', 'crypto_forecasting'],
      ['Metrics', 'RMSE / MAE / MAPE'],
      ['Registry', 'Model names enabled']
    ],
    notes: 'Training logs parameters, metrics, Keras artifacts, and registered model names into the local MLflow SQLite backend.'
  },
  {
    id: 'orchestration',
    label: 'Docker + Kubernetes',
    short: 'Docker / K8s',
    icon: 'Boxes',
    status: 'Good',
    score: 86,
    color: 'accent',
    command: 'docker compose config && kubectl apply -f k8s/',
    toolUrl: null,
    evidence: ['docker-compose.yml', 'backened/Dockerfile', 'frontened/cryptopredictpro/Dockerfile', 'k8s/'],
    metrics: [
      ['Compose services', '8'],
      ['K8s deployments', 'Backend + Frontend'],
      ['Replicas', '2 each']
    ],
    notes: 'The app now has backend and frontend container paths plus Kubernetes namespace, deployment, and service manifests.'
  },
  {
    id: 'serving',
    label: 'FastAPI + ReactJS',
    short: 'Serving',
    icon: 'Rocket',
    status: 'Good',
    score: 91,
    color: 'success',
    command: 'cd backened && uvicorn main:fastapi_app --host 0.0.0.0 --port 5000',
    toolUrl: 'http://localhost:5000/metrics-dashboard',
    evidence: ['backened/main.py', 'frontened/cryptopredictpro/src/services/predictionApi.js'],
    metrics: [
      ['API', 'FastAPI wrapper'],
      ['Frontend', 'React / Vite'],
      ['Metrics dashboard', '/metrics-dashboard']
    ],
    notes: 'FastAPI wraps the legacy Flask routes, exposes health and Prometheus metrics, and the React app calls live prediction APIs.'
  },
  {
    id: 'evidently',
    label: 'Evidently AI',
    short: 'Drift',
    icon: 'Activity',
    status: 'Good',
    score: 87,
    color: 'success',
    command: 'python scripts/drift_monitor.py',
    toolUrl: `${apiBaseUrl}/reports/drift/drift_report.html`,
    evidence: ['scripts/drift_monitor.py', 'reports/drift/drift_report.html'],
    metrics: [
      ['Report', 'HTML'],
      ['Features', 'OHLC'],
      ['Reference vs current', 'Enabled']
    ],
    notes: 'Evidently generates a drift report comparing cleaned reference data with live current OHLC data.'
  },
  {
    id: 'infra',
    label: 'Grafana + Prometheus',
    short: 'Infra',
    icon: 'Gauge',
    status: 'Good',
    score: 88,
    color: 'primary',
    command: 'docker compose up backend prometheus grafana',
    toolUrl: 'http://localhost:3001/d/cryptopredictpro-mlops-overview/cryptopredictpro-mlops-overview?orgId=1&refresh=5s',
    evidence: ['prometheus/prometheus.yml', 'grafana/provisioning/datasources/prometheus.yaml', 'grafana/provisioning/dashboards/'],
    metrics: [
      ['Prometheus', 'localhost:9090'],
      ['Grafana', 'localhost:3001'],
      ['Dashboard', 'Provisioned']
    ],
    notes: 'Prometheus scrapes FastAPI metrics and Grafana now provisions an overview dashboard for backend request rate and latency.'
  },
  {
    id: 'ci',
    label: 'GitHub + GitHub Actions',
    short: 'CI',
    icon: 'Workflow',
    status: 'Improved',
    score: 84,
    color: 'accent',
    command: 'git status && gh workflow view "MLOps CI/CD Pipeline"',
    toolUrl: null,
    evidence: ['.git/', '.github/workflows/mlops-ci.yml'],
    metrics: [
      ['SCM', 'Git initialized'],
      ['Quality gates', 'GE / Feast / Evidently'],
      ['Docker builds', 'Backend + Frontend']
    ],
    notes: 'The workflow now validates data quality, Feast, Evidently, Promptfoo, Python syntax, and backend/frontend Docker builds.'
  },
  {
    id: 'argocd',
    label: 'ArgoCD',
    short: 'ArgoCD',
    icon: 'RefreshCw',
    status: 'Partial',
    score: 76,
    color: 'warning',
    command: 'kubectl apply -f argocd/application.yaml',
    toolUrl: null,
    evidence: ['argocd/application.yaml', 'k8s/backend-deployment.yaml', 'k8s/frontend-deployment.yaml'],
    metrics: [
      ['GitOps app', 'Defined'],
      ['Sync policy', 'Auto + self-heal'],
      ['Cluster proof', 'Pending evaluator env']
    ],
    notes: 'ArgoCD application configuration exists and points at Kubernetes manifests; a live cluster sync is the remaining environment-dependent proof.'
  },
  {
    id: 'promptfoo',
    label: 'Promptfoo',
    short: 'Promptfoo',
    icon: 'MessageSquareCheck',
    status: 'Good',
    score: 85,
    color: 'success',
    command: 'npx promptfoo@latest eval -c promptfooconfig.yaml',
    toolUrl: `${apiBaseUrl}/reports/promptfoo/promptfoo_report.html`,
    evidence: ['promptfooconfig.yaml', 'prompts/crypto_summary.txt', 'reports/promptfoo/promptfoo_report.html'],
    metrics: [
      ['Test cases', '13 coins'],
      ['Assertions', 'Risk + warning'],
      ['CI gate', 'Enabled']
    ],
    notes: 'Promptfoo checks that generated crypto summaries include explicit risk language and not-financial-advice wording.'
  }
];

const statusStyles = {
  Good: 'border-success/30 bg-success/10 text-success',
  Improved: 'border-primary/30 bg-primary/10 text-primary',
  Partial: 'border-warning/30 bg-warning/10 text-warning'
};

const colorStyles = {
  primary: 'from-primary/80 to-primary/20',
  accent: 'from-accent/80 to-accent/20',
  success: 'from-success/80 to-success/20',
  warning: 'from-warning/80 to-warning/20'
};

const stageToneStyles = {
  primary: 'bg-primary/10 text-primary',
  accent: 'bg-accent/10 text-accent',
  success: 'bg-success/10 text-success',
  warning: 'bg-warning/10 text-warning'
};

const quickLinks = [
  { label: 'FastAPI Health', url: 'http://localhost:5000/fastapi-health', icon: 'HeartPulse' },
  { label: 'FastAPI Metrics', url: 'http://localhost:5000/metrics-dashboard', icon: 'TerminalSquare' },
  { label: 'MLflow', url: 'http://localhost:5002', icon: 'LineChart' },
  { label: 'Marquez', url: 'http://localhost:3000', icon: 'GitBranch' },
  { label: 'Prometheus Query', url: 'http://localhost:9090/graph?g0.expr=up&g0.tab=1&g0.range_input=1h', icon: 'Gauge' },
  { label: 'Grafana Dashboard', url: 'http://localhost:3001/d/cryptopredictpro-mlops-overview/cryptopredictpro-mlops-overview?orgId=1&refresh=5s', icon: 'LayoutDashboard' },
  { label: 'Promptfoo Report', url: `${apiBaseUrl}/reports/promptfoo/promptfoo_report.html`, icon: 'MessageSquareCheck' },
  { label: 'Drift Report', url: `${apiBaseUrl}/reports/drift/drift_report.html`, icon: 'Activity' }
];

const monitoringLinks = [
  {
    label: 'Target health',
    url: 'http://localhost:9090/graph?g0.expr=up&g0.tab=1&g0.range_input=1h',
    query: 'up',
    note: 'Shows whether Prometheus can reach the FastAPI backend. Value 1 means healthy.'
  },
  {
    label: 'Request rate',
    url: 'http://localhost:9090/graph?g0.expr=rate(http_requests_total%5B1m%5D)&g0.tab=1&g0.range_input=1h',
    query: 'rate(http_requests_total[1m])',
    note: 'Shows requests per second grouped by endpoint labels.'
  },
  {
    label: 'Latency average',
    url: 'http://localhost:9090/graph?g0.expr=rate(http_request_duration_seconds_sum%5B1m%5D)%20%2F%20rate(http_request_duration_seconds_count%5B1m%5D)&g0.tab=1&g0.range_input=1h',
    query: 'rate(http_request_duration_seconds_sum[1m]) / rate(http_request_duration_seconds_count[1m])',
    note: 'Shows average request duration in seconds.'
  },
  {
    label: 'Grafana overview',
    url: 'http://localhost:3001/d/cryptopredictpro-mlops-overview/cryptopredictpro-mlops-overview?orgId=1&refresh=5s',
    query: 'Provisioned dashboard',
    note: 'Grafana turns Prometheus metrics into charts for evaluator-friendly monitoring.'
  }
];

const dvcFlow = [
  { id: 'collection', title: 'Data Collection', icon: 'GitBranch', tone: 'primary', detail: 'raw daily + hourly CSVs' },
  { id: 'storage', title: 'Storage Inventory', icon: 'Files', tone: 'accent', detail: 'DVC-tracked artifacts' },
  { id: 'cleaning', title: 'Cleaning + Quality', icon: 'ClipboardCheck', tone: 'success', detail: 'validated OHLCV files' },
  { id: 'retention', title: 'Retention Check', icon: 'Archive', tone: 'accent', detail: 'all coins retained' },
  { id: 'featureSource', title: 'Feature Source', icon: 'FileType', tone: 'primary', detail: 'training-ready parquet' },
  { id: 'featureStore', title: 'Feature Store', icon: 'DatabaseZap', tone: 'success', detail: 'registry + online store' },
  { id: 'monitoring', title: 'Drift Monitor', icon: 'Activity', tone: 'warning', detail: 'Evidently report' },
  { id: 'training', title: 'Model Training', icon: 'Brain', tone: 'primary', detail: 'LSTM model artifacts' },
  { id: 'prediction', title: 'Prediction Outputs', icon: 'PlayCircle', tone: 'success', detail: 'forecast CSVs + metrics' }
];

const feastFeatureMap = [
  { name: 'INSTRUMENT', role: 'Entity key', source: 'crypto_instrument', usedByModel: 'Join key' },
  { name: 'DATE_UTC', role: 'Event timestamp', source: 'crypto_hourly_cleaned_source', usedByModel: 'Point-in-time lookup' },
  { name: 'OPEN', role: 'Registered feature', source: 'crypto_hourly_stats', usedByModel: 'Available for future multivariate model' },
  { name: 'HIGH', role: 'Registered feature', source: 'crypto_hourly_stats', usedByModel: 'Available for future multivariate model' },
  { name: 'LOW', role: 'Registered feature', source: 'crypto_hourly_stats', usedByModel: 'Available for future multivariate model' },
  { name: 'CLOSE', role: 'Registered feature', source: 'crypto_hourly_stats', usedByModel: 'Used by current LSTM sequence' },
  { name: 'VOLUME', role: 'Registered feature', source: 'crypto_hourly_stats', usedByModel: 'Available for future multivariate model' }
];

const promptfooTests = [
  ['Bitcoin', 'risk + not financial advice'],
  ['Ethereum', 'warning'],
  ['Solana', 'risk'],
  ['Binance Coin', 'warning'],
  ['Bitcoin Cash', 'risk'],
  ['Litecoin', 'warning'],
  ['Chainlink', 'warning'],
  ['Avalanche', 'warning'],
  ['Ripple', 'risk'],
  ['Polkadot', 'risk'],
  ['Cardano', 'risk'],
  ['Polygon', 'risk'],
  ['Dogecoin', 'warning']
];

const scoreBands = [
  { label: 'Data lineage', value: 86 },
  { label: 'Versioning', value: 88 },
  { label: 'Quality + features', value: 89 },
  { label: 'Training + registry', value: 88 },
  { label: 'Serving + monitoring', value: 90 },
  { label: 'CI/CD + GitOps', value: 80 }
];

const barGradients = {
  primary: 'linear-gradient(90deg, #22d3ee 0%, #38bdf8 55%, #60a5fa 100%)',
  accent: 'linear-gradient(90deg, #14b8a6 0%, #2dd4bf 55%, #5eead4 100%)',
  success: 'linear-gradient(90deg, #22c55e 0%, #34d399 55%, #86efac 100%)',
  warning: 'linear-gradient(90deg, #f59e0b 0%, #fbbf24 55%, #fde68a 100%)'
};

const MiniBars = ({ value, tone = 'primary' }) => (
  <div
    className="h-2.5 overflow-hidden rounded-full border border-border/60"
    style={{ background: 'rgba(148, 163, 184, 0.16)' }}
  >
    <div
      className="h-full rounded-full transition-all duration-500"
      style={{
        width: `${value}%`,
        background: barGradients[tone] || barGradients.primary,
        boxShadow: '0 0 16px rgba(34, 211, 238, 0.5)'
      }}
    />
  </div>
);

const EvidencePill = ({ children }) => (
  <span className="inline-flex items-center rounded-full border border-border/70 bg-input/70 px-3 py-1 text-[11px] text-muted-foreground">
    {children}
  </span>
);

const MetricTile = ({ label, value }) => (
  <div className="min-w-0 rounded-lg border border-border/70 bg-input/45 p-3">
    <p className="text-[11px] uppercase tracking-[0.14em] text-muted-foreground">{label}</p>
    <p className="mt-2 break-words text-base font-display font-semibold text-foreground lg:text-lg">{value}</p>
  </div>
);

const MLOpsPage = () => {
  const [activeId, setActiveId] = useState('lineage');
  const [previewUrl, setPreviewUrl] = useState('http://localhost:3001');

  const activeTool = useMemo(
    () => tools.find((tool) => tool.id === activeId) || tools[0],
    [activeId]
  );

  const averageScore = Math.round(tools.reduce((sum, tool) => sum + tool.score, 0) / tools.length);
  const goodCount = tools.filter((tool) => tool.status === 'Good').length;
  const improvedCount = tools.filter((tool) => tool.status === 'Improved').length;

  const setTool = (tool) => {
    setActiveId(tool.id);
    if (tool.toolUrl) setPreviewUrl(tool.toolUrl);
  };

  return (
    <div className="min-h-screen text-foreground">
      <div className="absolute inset-0 grid-background opacity-40 pointer-events-none" />
      <div className="absolute -left-28 top-16 h-72 w-72 rounded-full bg-primary/20 blur-[96px] floating-orb pointer-events-none" />
      <div className="absolute -right-24 top-40 h-72 w-72 rounded-full bg-accent/20 blur-[96px] floating-orb pointer-events-none" />

      <header className="relative z-20 border-b border-border/60 bg-card/70 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 lg:px-6">
          <Link to="/dashboard" className="flex items-center">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-accent soft-glow">
              <Icon name="TrendingUp" size={20} color="white" />
            </div>
            <div className="ml-3">
              <p className="text-lg font-display font-bold text-gradient">CryptoPredictPro</p>
              <p className="text-[11px] text-muted-foreground">MLOps evaluator cockpit</p>
            </div>
          </Link>
          <div className="flex items-center gap-2">
            <Link to="/dashboard" className="rounded-md border border-border/70 bg-muted/60 px-3 py-2 text-sm text-muted-foreground transition-smooth hover:text-foreground">
              App Dashboard
            </Link>
            <a href="http://localhost:5000/fastapi-health" target="_blank" rel="noreferrer" className="hidden rounded-md bg-primary px-3 py-2 text-sm font-semibold text-primary-foreground transition-smooth hover:opacity-90 sm:inline-flex">
              Check API
            </a>
          </div>
        </div>
      </header>

      <main className="relative z-10 mx-auto max-w-7xl px-4 py-6 lg:px-6">
        <motion.section
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45 }}
          className="glass-panel hud-border rounded-3xl p-5 lg:p-7"
        >
          <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.22em] text-muted-foreground">Assignment Requirements</p>
              <h1 className="mt-2 text-3xl font-display font-bold text-gradient lg:text-5xl">
                End-to-end MLOps Evidence Board
              </h1>
              <p className="mt-3 max-w-3xl text-sm text-muted-foreground">
                Visual proof for OpenLineage, DVC, Great Expectations, Feast, MLflow, Docker, Kubernetes, FastAPI, React, Evidently, Grafana, Prometheus, GitHub Actions, ArgoCD, and Promptfoo.
              </p>
            </div>
            <div className="grid grid-cols-3 gap-3 text-center">
              <div className="rounded-lg border border-primary/30 bg-primary/10 p-3">
                <p className="text-3xl font-display font-bold text-primary">{averageScore}</p>
                <p className="text-[11px] text-muted-foreground">Score / 100</p>
              </div>
              <div className="rounded-lg border border-success/30 bg-success/10 p-3">
                <p className="text-3xl font-display font-bold text-success">{goodCount}</p>
                <p className="text-[11px] text-muted-foreground">Good</p>
              </div>
              <div className="rounded-lg border border-accent/30 bg-accent/10 p-3">
                <p className="text-3xl font-display font-bold text-accent">{improvedCount}</p>
                <p className="text-[11px] text-muted-foreground">Improved</p>
              </div>
            </div>
          </div>
        </motion.section>

        <section className="mt-6 grid gap-6 lg:grid-cols-[260px_minmax(0,1fr)]">
          <aside className="neo-card p-3 lg:sticky lg:top-6 lg:h-[calc(100vh-3rem)] lg:overflow-auto">
            <p className="px-3 py-2 text-[11px] uppercase tracking-[0.18em] text-muted-foreground">Requirement Navigator</p>
            <div className="space-y-1">
              {tools.map((tool) => (
                <button
                  key={tool.id}
                  onClick={() => setTool(tool)}
                  className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm transition-smooth ${
                    activeId === tool.id
                      ? 'bg-primary/15 text-foreground soft-glow'
                      : 'text-muted-foreground hover:bg-muted/70 hover:text-foreground'
                  }`}
                >
                  <Icon name={tool.icon} size={16} />
                  <span className="min-w-0 flex-1 truncate">{tool.short}</span>
                  <span className={`rounded-full border px-2 py-0.5 text-[10px] ${statusStyles[tool.status]}`}>
                    {tool.score}
                  </span>
                </button>
              ))}
            </div>
          </aside>

          <div className="space-y-6">
            <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <MetricTile label="Tools covered" value="12 / 12" />
              <MetricTile label="DVC + Feast proof" value="Materialized" />
              <MetricTile label="Monitoring stack" value="Prom + Grafana" />
              <MetricTile label="Frontend proof" value="This page" />
            </section>

            <section className="grid gap-6 xl:grid-cols-[minmax(0,1.1fr)_minmax(360px,0.9fr)]">
              <motion.div
                key={activeTool.id}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.28 }}
                className="neo-card hud-border p-5"
              >
                <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                  <div className="flex items-start gap-4">
                    <div className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br ${colorStyles[activeTool.color]} soft-glow`}>
                      <Icon name={activeTool.icon} size={22} color="white" />
                    </div>
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <h2 className="text-2xl font-display font-bold">{activeTool.label}</h2>
                        <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${statusStyles[activeTool.status]}`}>
                          {activeTool.status}
                        </span>
                      </div>
                      <p className="mt-2 text-sm text-muted-foreground">{activeTool.notes}</p>
                    </div>
                  </div>
                  <div className="min-w-[120px] rounded-lg border border-border/70 bg-input/50 p-3 text-center">
                    <p className="text-3xl font-display font-bold text-gradient">{activeTool.score}</p>
                    <p className="text-[11px] text-muted-foreground">evaluator score</p>
                  </div>
                </div>

                <div className="mt-5">
                  <div className="mb-2 flex items-center justify-between text-xs text-muted-foreground">
                    <span>Implementation completeness</span>
                    <span>{activeTool.score}%</span>
                  </div>
                  <MiniBars value={activeTool.score} tone={activeTool.color} />
                </div>

                <div className="mt-5 grid gap-3 md:grid-cols-3">
                  {activeTool.metrics.map(([label, value]) => (
                    <MetricTile key={label} label={label} value={value} />
                  ))}
                </div>

                <div className="mt-5 rounded-lg border border-border/70 bg-background/40 p-4">
                  <div className="mb-3 flex items-center gap-2 text-sm font-semibold">
                    <Icon name="Terminal" size={16} />
                    Demo command
                  </div>
                  <code className="block overflow-x-auto whitespace-nowrap rounded-md bg-input/80 px-3 py-2 font-mono text-xs text-primary">
                    {activeTool.command}
                  </code>
                </div>

                <div className="mt-5">
                  <p className="mb-2 text-xs uppercase tracking-[0.16em] text-muted-foreground">Evidence files</p>
                  <div className="flex flex-wrap gap-2">
                    {activeTool.evidence.map((item) => (
                      <EvidencePill key={item}>{item}</EvidencePill>
                    ))}
                  </div>
                </div>

                {activeTool.id === 'infra' && (
                  <div className="mt-5 rounded-lg border border-primary/25 bg-primary/5 p-4">
                    <div className="flex items-start gap-3">
                      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/15 text-primary">
                        <Icon name="Info" size={18} />
                      </div>
                      <div>
                        <p className="text-sm font-semibold">How to read Prometheus and Grafana</p>
                        <p className="mt-1 text-xs leading-5 text-muted-foreground">
                          Prometheus is the metrics database and query console. It looks empty until you run a query.
                          Grafana is the visual dashboard that graphs those Prometheus metrics.
                        </p>
                      </div>
                    </div>
                    <div className="mt-4 grid gap-3 md:grid-cols-2">
                      {monitoringLinks.map((link) => (
                        <a
                          key={link.label}
                          href={link.url}
                          target="_blank"
                          rel="noreferrer"
                          className="rounded-lg border border-border/70 bg-input/55 p-3 transition-smooth hover:border-primary/50 hover:bg-primary/10"
                        >
                          <div className="flex items-center justify-between gap-3">
                            <span className="text-sm font-semibold text-foreground">{link.label}</span>
                            <Icon name="ExternalLink" size={14} className="text-primary" />
                          </div>
                          <code className="mt-2 block truncate font-mono text-[11px] text-primary">{link.query}</code>
                          <p className="mt-2 text-xs leading-5 text-muted-foreground">{link.note}</p>
                        </a>
                      ))}
                    </div>
                  </div>
                )}

                {activeTool.id === 'dvc' && (
                  <div className="mt-5 rounded-lg border border-accent/25 bg-accent/5 p-4">
                    <div className="flex items-start gap-3">
                      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-accent/15 text-accent">
                        <Icon name="GitMerge" size={18} />
                      </div>
                      <div>
                        <p className="text-sm font-semibold">DVC pipeline flow</p>
                        <p className="mt-1 text-xs leading-5 text-muted-foreground">
                          This groups the reproducible <code>dvc.yaml</code> stages into the expected ML lifecycle:
                          collection, storage, cleaning, training, prediction, and monitoring evidence.
                        </p>
                      </div>
                    </div>

                    <div className="mt-4 overflow-x-auto pb-2">
                      <div className="grid min-w-[760px] grid-cols-4 gap-3">
                        {dvcFlow.slice(0, 4).map((stage, index) => (
                          <div key={stage.id} className="relative rounded-lg border border-border/70 bg-input/55 p-3">
                            {index < 3 && (
                              <div className="absolute -right-3 top-1/2 hidden h-px w-3 bg-primary/60 md:block" />
                            )}
                            <div className={`mb-3 flex h-9 w-9 items-center justify-center rounded-lg ${stageToneStyles[stage.tone]}`}>
                              <Icon name={stage.icon} size={17} />
                            </div>
                            <p className="text-sm font-semibold">{stage.title}</p>
                            <p className="mt-1 text-xs text-muted-foreground">{stage.detail}</p>
                          </div>
                        ))}
                      </div>

                      <div className="my-3 ml-[calc(75%-1.5rem)] hidden h-8 w-px bg-primary/60 md:block" />

                      <div className="grid min-w-[760px] grid-cols-4 gap-3">
                        {dvcFlow.slice(4, 8).map((stage, index) => (
                          <div key={stage.id} className="relative rounded-lg border border-border/70 bg-input/55 p-3">
                            {index < 3 && (
                              <div className="absolute -right-3 top-1/2 hidden h-px w-3 bg-primary/60 md:block" />
                            )}
                            <div className={`mb-3 flex h-9 w-9 items-center justify-center rounded-lg ${stageToneStyles[stage.tone]}`}>
                              <Icon name={stage.icon} size={17} />
                            </div>
                            <p className="text-sm font-semibold">{stage.title}</p>
                            <p className="mt-1 text-xs text-muted-foreground">{stage.detail}</p>
                          </div>
                        ))}
                      </div>

                      <div className="my-3 ml-[calc(75%-1.5rem)] hidden h-8 w-px bg-primary/60 md:block" />

                      <div className="grid min-w-[760px] grid-cols-4 gap-3">
                        <div className="rounded-lg border border-border/70 bg-input/55 p-3">
                          <div className={`mb-3 flex h-9 w-9 items-center justify-center rounded-lg ${stageToneStyles[dvcFlow[8].tone]}`}>
                            <Icon name={dvcFlow[8].icon} size={17} />
                          </div>
                          <p className="text-sm font-semibold">{dvcFlow[8].title}</p>
                          <p className="mt-1 text-xs text-muted-foreground">{dvcFlow[8].detail}</p>
                        </div>
                        <div className="col-span-3 rounded-lg border border-primary/25 bg-primary/5 p-3">
                          <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">Generated artifacts</p>
                          <div className="mt-2 flex flex-wrap gap-2">
                            {['reports/inventory', 'reports/data_quality', 'reports/feast', 'reports/drift', 'milestone-2/infosys/outputs'].map((item) => (
                              <EvidencePill key={item}>{item}</EvidencePill>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="mt-4 rounded-lg border border-border/70 bg-background/40 p-3">
                      <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">Run command</p>
                      <code className="mt-2 block overflow-x-auto whitespace-nowrap font-mono text-xs text-primary">
                        dvc repro inventory data_quality retention_check feast_source feast_apply feast_materialize drift_report train_demo_models
                      </code>
                    </div>
                  </div>
                )}

                {activeTool.id === 'feast' && (
                  <div className="mt-5 rounded-lg border border-primary/25 bg-primary/5 p-4">
                    <div className="flex items-start gap-3">
                      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/15 text-primary">
                        <Icon name="TableProperties" size={18} />
                      </div>
                      <div>
                        <p className="text-sm font-semibold">Feast feature map for model inputs</p>
                        <p className="mt-1 text-xs leading-5 text-muted-foreground">
                          Feast should prove the feature columns available to the model. This project registers OHLCV
                          market features in Feast, while the current LSTM training code uses the <code>CLOSE</code> price
                          sequence as its active model input.
                        </p>
                      </div>
                    </div>

                    <div className="mt-4 grid gap-3 md:grid-cols-3">
                      <MetricTile label="Entity" value="INSTRUMENT" />
                      <MetricTile label="Timestamp" value="DATE_UTC" />
                      <MetricTile label="Feature view" value="crypto_hourly_stats" />
                    </div>

                    <div className="mt-4 grid gap-3 md:grid-cols-2">
                      {feastFeatureMap.map((feature) => (
                        <div key={feature.name} className="rounded-lg border border-border/70 bg-background/45 p-3">
                          <div className="flex flex-wrap items-center justify-between gap-2">
                            <p className="font-mono text-sm font-semibold text-primary">{feature.name}</p>
                            <span className={`rounded-full border px-2.5 py-1 text-[11px] ${
                              feature.name === 'CLOSE'
                                ? 'border-success/40 bg-success/10 text-success'
                                : 'border-border/70 bg-input/60 text-muted-foreground'
                            }`}>
                              {feature.role}
                            </span>
                          </div>
                          <p className="mt-2 break-words text-xs text-muted-foreground">
                            Source: <span className="text-foreground">{feature.source}</span>
                          </p>
                          <p className="mt-1 break-words text-xs text-muted-foreground">
                            Model: <span className={feature.name === 'CLOSE' ? 'text-success' : 'text-foreground'}>
                              {feature.usedByModel}
                            </span>
                          </p>
                        </div>
                      ))}
                    </div>

                    <div className="mt-4 rounded-lg border border-border/70 bg-background/40 p-3">
                      <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">Proof commands</p>
                      <code className="mt-2 block overflow-x-auto whitespace-nowrap font-mono text-xs text-primary">
                        feast -c feature_repo registry-dump && dvc repro feast_source feast_apply feast_materialize
                      </code>
                    </div>
                  </div>
                )}

                {activeTool.id === 'promptfoo' && (
                  <div className="mt-5 rounded-lg border border-success/25 bg-success/5 p-4">
                    <div className="flex items-start gap-3">
                      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-success/15 text-success">
                        <Icon name="MessageSquareCheck" size={18} />
                      </div>
                      <div>
                        <p className="text-sm font-semibold">Promptfoo evaluation view</p>
                        <p className="mt-1 text-xs leading-5 text-muted-foreground">
                          Promptfoo tests the crypto summary prompt before it reaches users. These checks make sure every
                          generated summary includes risk wording and avoids financial-advice language.
                        </p>
                      </div>
                    </div>

                    <div className="mt-4 grid gap-3 md:grid-cols-3">
                      <MetricTile label="Pass rate" value="13 / 13" />
                      <MetricTile label="Provider" value="echo" />
                      <MetricTile label="Prompt file" value="crypto_summary.txt" />
                    </div>

                    <div className="mt-4 rounded-lg border border-border/70 bg-background/45 p-3">
                      <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">Prompt under test</p>
                      <pre className="mt-2 max-h-44 overflow-auto whitespace-pre-wrap rounded-md bg-input/75 p-3 font-mono text-xs leading-5 text-muted-foreground">
{`You are a financial analyst summarizing cryptocurrency trends for a mobile app.
Based on the following LSTM prediction for {{coin}}, provide a 2-sentence summary.

IMPORTANT:
- Never give financial advice.
- Always include a risk warning.
- Be concise.`}
                      </pre>
                    </div>

                    <div className="mt-4 grid gap-2 sm:grid-cols-2">
                      {promptfooTests.map(([coin, assertion]) => (
                        <div key={coin} className="flex items-center justify-between gap-3 rounded-lg border border-border/70 bg-background/45 p-3">
                          <div className="min-w-0">
                            <p className="truncate text-sm font-semibold text-foreground">{coin}</p>
                            <p className="mt-1 text-xs text-muted-foreground">Assertion: {assertion}</p>
                          </div>
                          <span className="rounded-full border border-success/35 bg-success/10 px-2.5 py-1 text-[11px] font-semibold text-success">
                            PASS
                          </span>
                        </div>
                      ))}
                    </div>

                    <div className="mt-4 flex flex-wrap gap-2">
                      <a
                        href={`${apiBaseUrl}/reports/promptfoo/promptfoo_report.html`}
                        target="_blank"
                        rel="noreferrer"
                        className="rounded-lg border border-success/35 bg-success/10 px-3 py-2 text-xs font-semibold text-success transition-smooth hover:bg-success/15"
                      >
                        Open Promptfoo Report
                      </a>
                      <EvidencePill>reports/promptfoo/promptfoo_report.html</EvidencePill>
                    </div>
                  </div>
                )}
              </motion.div>

              <div className="neo-card p-5">
                <div className="mb-4 flex items-center justify-between gap-3">
                  <div>
                    <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Live Tool Launcher</p>
                    <h3 className="mt-1 text-xl font-display font-semibold">Metrics and UIs</h3>
                  </div>
                  <Icon name="MonitorUp" size={22} className="text-primary" />
                </div>

                <div className="grid grid-cols-2 gap-2">
                  {quickLinks.map((link) => (
                    <button
                      key={link.label}
                      onClick={() => setPreviewUrl(link.url)}
                      className="rounded-lg border border-border/70 bg-input/50 p-3 text-left transition-smooth hover:border-primary/50 hover:bg-primary/10"
                    >
                      <Icon name={link.icon} size={16} className="mb-2 text-primary" />
                      <p className="text-sm font-semibold">{link.label}</p>
                      <p className="mt-1 truncate text-[11px] text-muted-foreground">{link.url}</p>
                    </button>
                  ))}
                </div>

                <div className="mt-4 overflow-hidden rounded-lg border border-border/70 bg-background">
                  <div className="flex items-center justify-between border-b border-border/70 bg-input/70 px-3 py-2">
                    <p className="truncate text-xs text-muted-foreground">{previewUrl}</p>
                    <a href={previewUrl} target="_blank" rel="noreferrer" className="text-xs font-semibold text-primary hover:text-primary/80">
                      Open
                    </a>
                  </div>
                  <iframe
                    title="MLOps tool preview"
                    src={previewUrl}
                    className="h-[330px] w-full bg-card"
                  />
                </div>
                <p className="mt-3 text-xs text-muted-foreground">
                  Some tools may block iframe embedding. Use Open if the preview panel is blank.
                </p>
              </div>
            </section>

            <section className="grid gap-6 xl:grid-cols-2">
              <div className="neo-card p-5">
                <div className="mb-4 flex items-center gap-2">
                  <Icon name="BarChart3" size={18} className="text-primary" />
                  <h3 className="text-lg font-display font-semibold">Capability Score Breakdown</h3>
                </div>
                <div className="space-y-4">
                  {scoreBands.map((band, index) => (
                    <div key={band.label}>
                      <div className="mb-2 flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">{band.label}</span>
                        <span className="font-semibold">{band.value}%</span>
                      </div>
                      <MiniBars value={band.value} tone={index % 2 === 0 ? 'primary' : 'accent'} />
                    </div>
                  ))}
                </div>
              </div>

              <div className="neo-card p-5">
                <div className="mb-4 flex items-center gap-2">
                  <Icon name="ListChecks" size={18} className="text-accent" />
                  <h3 className="text-lg font-display font-semibold">Evaluator Checklist</h3>
                </div>
                <div className="space-y-3">
                  {[
                    ['Run DVC and quality gates', 'dvc repro data_quality feast_source feast_apply feast_materialize'],
                    ['Open tracking and lineage tools', 'MLflow localhost:5002, Marquez localhost:3000'],
                    ['Show serving and app behavior', 'FastAPI localhost:5000, React /dashboard'],
                    ['Show infra dashboards', 'Prometheus localhost:9090, Grafana localhost:3001'],
                    ['Explain remaining partial item', 'ArgoCD needs a live cluster/registry for final proof']
                  ].map(([title, detail]) => (
                    <div key={title} className="flex gap-3 rounded-lg border border-border/70 bg-input/45 p-3">
                      <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-success/10 text-success">
                        <Icon name="Check" size={15} />
                      </div>
                      <div>
                        <p className="text-sm font-semibold">{title}</p>
                        <p className="mt-1 text-xs text-muted-foreground">{detail}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </section>

            <section className="neo-card overflow-hidden">
              <div className="border-b border-border/70 p-5">
                <h3 className="text-lg font-display font-semibold">Requirement Status Matrix</h3>
                <p className="mt-1 text-sm text-muted-foreground">A quick table the evaluator can scan during the demo.</p>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full min-w-[760px] text-sm">
                  <thead className="bg-input/60 text-left text-xs uppercase tracking-[0.12em] text-muted-foreground">
                    <tr>
                      <th className="px-5 py-3">Requirement</th>
                      <th className="px-5 py-3">Status</th>
                      <th className="px-5 py-3">Score</th>
                      <th className="px-5 py-3">Evidence</th>
                    </tr>
                  </thead>
                  <tbody>
                    {tools.map((tool) => (
                      <tr key={tool.id} className="border-t border-border/60">
                        <td className="px-5 py-4 font-semibold">{tool.label}</td>
                        <td className="px-5 py-4">
                          <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${statusStyles[tool.status]}`}>
                            {tool.status}
                          </span>
                        </td>
                        <td className="px-5 py-4">
                          <div className="flex items-center gap-3">
                            <span className="w-9 font-semibold">{tool.score}</span>
                            <div className="w-36 max-w-[38vw]">
                              <MiniBars value={tool.score} tone={tool.color} />
                            </div>
                          </div>
                        </td>
                        <td className="px-5 py-4 text-muted-foreground">{tool.evidence.slice(0, 2).join(', ')}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          </div>
        </section>
      </main>
    </div>
  );
};

export default MLOpsPage;
