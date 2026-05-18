import re
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
from fastapi.responses import HTMLResponse
from app import app as flask_app

APP_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = APP_ROOT.parent if APP_ROOT.name.lower() == "backened" else APP_ROOT
REPORTS_DIR = PROJECT_ROOT / "reports"

# Initialize FastAPI application
fastapi_app = FastAPI(
    title="Cryptocurrency Price Forecasting API",
    description="MLOps implementation with FastAPI wrapping existing Flask services.",
    version="2.0.0"
)

# Add CORS middleware to FastAPI
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@fastapi_app.get("/fastapi-health")
async def fastapi_health():
    """A native async FastAPI health check endpoint."""
    return {"status": "FastAPI is running alongside Flask"}

# Initialize Prometheus Instrumentator
Instrumentator().instrument(fastapi_app)

@fastapi_app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


SAMPLE_RE = re.compile(r'^(?P<name>[a-zA-Z_:][a-zA-Z0-9_:]*)(?:\{(?P<labels>[^}]*)\})?\s+(?P<value>[-+0-9.eE]+)$')
LABEL_RE = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)="([^"]*)"')


def parse_prometheus_samples() -> list[dict]:
    rows = []
    for raw_line in generate_latest().decode("utf-8", errors="ignore").splitlines():
        if not raw_line or raw_line.startswith("#"):
            continue
        match = SAMPLE_RE.match(raw_line.strip())
        if not match:
            continue
        labels = dict(LABEL_RE.findall(match.group("labels") or ""))
        try:
            value = float(match.group("value"))
        except ValueError:
            continue
        rows.append({"name": match.group("name"), "labels": labels, "value": value})
    return rows


@fastapi_app.get("/metrics-summary")
def metrics_summary():
    samples = parse_prometheus_samples()
    request_count = 0.0
    request_sum = 0.0
    response_bytes = 0.0
    handlers = {}

    for sample in samples:
        name = sample["name"]
        labels = sample["labels"]
        value = sample["value"]
        handler = labels.get("handler", "all")

        if name == "http_requests_total":
            request_count += value
            handlers.setdefault(handler, {"requests": 0.0, "latency_sum": 0.0, "latency_count": 0.0})
            handlers[handler]["requests"] += value
        elif name == "http_request_duration_seconds_sum":
            request_sum += value
            handlers.setdefault(handler, {"requests": 0.0, "latency_sum": 0.0, "latency_count": 0.0})
            handlers[handler]["latency_sum"] += value
        elif name == "http_request_duration_seconds_count":
            handlers.setdefault(handler, {"requests": 0.0, "latency_sum": 0.0, "latency_count": 0.0})
            handlers[handler]["latency_count"] += value
        elif name == "http_response_size_bytes_sum":
            response_bytes += value

    avg_latency_ms = (request_sum / request_count * 1000.0) if request_count else 0.0
    handler_rows = []
    for handler, data in handlers.items():
        latency_count = data["latency_count"]
        handler_rows.append(
            {
                "handler": handler,
                "requests": round(data["requests"], 2),
                "avg_latency_ms": round(data["latency_sum"] / latency_count * 1000.0, 2) if latency_count else 0.0,
            }
        )
    handler_rows.sort(key=lambda item: item["requests"], reverse=True)

    return {
        "status": "online",
        "total_requests": round(request_count, 2),
        "avg_latency_ms": round(avg_latency_ms, 2),
        "response_bytes": round(response_bytes, 2),
        "sample_count": len(samples),
        "handlers": handler_rows[:8],
    }


@fastapi_app.get("/metrics-dashboard", response_class=HTMLResponse)
def metrics_dashboard():
    return """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>CryptoPredictPro FastAPI Metrics</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #030916;
      --panel: rgba(7, 20, 40, 0.82);
      --panel-2: rgba(14, 28, 51, 0.78);
      --border: rgba(97, 130, 176, 0.25);
      --text: #e8f0ff;
      --muted: #8ea4c2;
      --primary: #24b8ff;
      --accent: #14d5b8;
      --success: #29dca4;
      --warning: #ffbe47;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--text);
      background:
        radial-gradient(44rem 32rem at -4% -6%, rgba(36, 184, 255, 0.24), transparent),
        radial-gradient(40rem 28rem at 110% -10%, rgba(20, 213, 184, 0.22), transparent),
        linear-gradient(180deg, #030916 0%, #030d1b 42%, #041024 100%);
    }
    .grid {
      position: fixed;
      inset: 0;
      pointer-events: none;
      opacity: 0.45;
      background-image:
        linear-gradient(rgba(97, 130, 176, 0.08) 1px, transparent 1px),
        linear-gradient(90deg, rgba(97, 130, 176, 0.07) 1px, transparent 1px);
      background-size: 40px 40px;
    }
    main { position: relative; max-width: 1180px; margin: 0 auto; padding: 28px 18px; }
    .hero, .card {
      border: 1px solid var(--border);
      background: linear-gradient(150deg, rgba(13, 31, 57, 0.78), rgba(7, 20, 40, 0.84));
      box-shadow: 0 24px 48px rgba(2, 9, 24, 0.48);
      backdrop-filter: blur(16px);
      border-radius: 18px;
    }
    .hero { padding: 26px; display: flex; justify-content: space-between; gap: 20px; align-items: flex-end; }
    h1 { margin: 0; font-size: clamp(28px, 4vw, 46px); letter-spacing: -0.03em; }
    .gradient { background: linear-gradient(95deg, #b8ebff, #8be3da 52%, #7cbcff); -webkit-background-clip: text; color: transparent; }
    .sub { color: var(--muted); margin: 10px 0 0; line-height: 1.55; }
    .status {
      display: inline-flex;
      gap: 8px;
      align-items: center;
      border: 1px solid rgba(41, 220, 164, 0.35);
      background: rgba(41, 220, 164, 0.12);
      color: var(--success);
      border-radius: 999px;
      padding: 8px 12px;
      font-weight: 700;
      white-space: nowrap;
    }
    .dot { width: 8px; height: 8px; border-radius: 999px; background: var(--success); box-shadow: 0 0 18px var(--success); }
    .cards { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; margin-top: 16px; }
    .card { padding: 18px; }
    .label { color: var(--muted); text-transform: uppercase; letter-spacing: 0.12em; font-size: 11px; }
    .value { margin-top: 10px; font-size: 30px; font-weight: 800; letter-spacing: -0.03em; }
    .bar { height: 8px; margin-top: 14px; border-radius: 999px; background: rgba(142, 164, 194, 0.16); overflow: hidden; }
    .fill { height: 100%; border-radius: inherit; background: linear-gradient(90deg, var(--primary), var(--accent)); transition: width 0.45s ease; }
    .layout { display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 16px; margin-top: 16px; }
    table { width: 100%; border-collapse: collapse; font-size: 13px; }
    th, td { text-align: left; padding: 12px 10px; border-bottom: 1px solid rgba(97, 130, 176, 0.18); }
    th { color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.12em; }
    tr:last-child td { border-bottom: 0; }
    .actions { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 16px; }
    a, button {
      color: var(--text);
      border: 1px solid var(--border);
      background: var(--panel-2);
      border-radius: 10px;
      padding: 10px 12px;
      text-decoration: none;
      font-weight: 700;
      cursor: pointer;
    }
    a.primary, button.primary { color: #031220; background: var(--primary); border-color: var(--primary); }
    .raw {
      margin-top: 12px;
      max-height: 280px;
      overflow: auto;
      padding: 12px;
      background: rgba(0, 0, 0, 0.28);
      border: 1px solid rgba(97, 130, 176, 0.2);
      border-radius: 12px;
      color: #cde8ff;
      font: 12px/1.55 ui-monospace, SFMono-Regular, Consolas, monospace;
      white-space: pre;
    }
    @media (max-width: 850px) {
      .hero { display: block; }
      .status { margin-top: 16px; }
      .cards, .layout { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="grid"></div>
  <main>
    <section class="hero">
      <div>
        <div class="label">FastAPI / Prometheus</div>
        <h1 class="gradient">Metrics Dashboard</h1>
        <p class="sub">Human-readable view for the FastAPI metrics endpoint. Prometheus still scrapes the raw <code>/metrics</code> route.</p>
      </div>
      <div class="status"><span class="dot"></span><span id="status">Loading</span></div>
    </section>

    <section class="cards">
      <div class="card"><div class="label">Total requests</div><div class="value" id="requests">--</div><div class="bar"><div class="fill" id="requestsBar"></div></div></div>
      <div class="card"><div class="label">Avg latency</div><div class="value" id="latency">--</div><div class="bar"><div class="fill" id="latencyBar"></div></div></div>
      <div class="card"><div class="label">Metric samples</div><div class="value" id="samples">--</div><div class="bar"><div class="fill" id="samplesBar"></div></div></div>
      <div class="card"><div class="label">Response bytes</div><div class="value" id="bytes">--</div><div class="bar"><div class="fill" id="bytesBar"></div></div></div>
    </section>

    <section class="layout">
      <div class="card">
        <div class="label">Handler activity</div>
        <table>
          <thead><tr><th>Handler</th><th>Requests</th><th>Avg latency</th></tr></thead>
          <tbody id="handlerRows"><tr><td colspan="3">Loading...</td></tr></tbody>
        </table>
      </div>
      <div class="card">
        <div class="label">Tool links</div>
        <div class="actions">
          <a class="primary" href="/docs">FastAPI Docs</a>
          <a href="/metrics">Raw Prometheus</a>
          <a href="/fastapi-health">Health</a>
          <button onclick="loadMetrics()">Refresh</button>
        </div>
        <div class="raw" id="rawPreview">Loading raw preview...</div>
      </div>
    </section>
  </main>
  <script>
    const fmt = new Intl.NumberFormat();
    const setWidth = (id, value, max) => {
      document.getElementById(id).style.width = Math.max(6, Math.min(100, value / max * 100)) + "%";
    };
    async function loadMetrics() {
      const summary = await fetch("/metrics-summary").then((res) => res.json());
      document.getElementById("status").textContent = summary.status.toUpperCase();
      document.getElementById("requests").textContent = fmt.format(summary.total_requests);
      document.getElementById("latency").textContent = summary.avg_latency_ms + " ms";
      document.getElementById("samples").textContent = fmt.format(summary.sample_count);
      document.getElementById("bytes").textContent = fmt.format(Math.round(summary.response_bytes));
      setWidth("requestsBar", summary.total_requests, 500);
      setWidth("latencyBar", summary.avg_latency_ms, 250);
      setWidth("samplesBar", summary.sample_count, 800);
      setWidth("bytesBar", summary.response_bytes, 50000);

      document.getElementById("handlerRows").innerHTML = summary.handlers.map((row) => `
        <tr>
          <td>${row.handler}</td>
          <td>${fmt.format(row.requests)}</td>
          <td>${row.avg_latency_ms} ms</td>
        </tr>
      `).join("") || '<tr><td colspan="3">No handler samples yet</td></tr>';

      const raw = await fetch("/metrics").then((res) => res.text());
      document.getElementById("rawPreview").textContent = raw.split("\\n").slice(0, 18).join("\\n");
    }
    loadMetrics();
    setInterval(loadMetrics, 5000);
  </script>
</body>
</html>
"""

# Serve generated MLOps reports before the Flask catch-all mount.
if REPORTS_DIR.exists():
    fastapi_app.mount("/reports", StaticFiles(directory=REPORTS_DIR), name="reports")


# Mount the existing Flask app to handle all legacy routes
# This is the "Strangler Fig Pattern" for migrating legacy applications
fastapi_app.mount("/", WSGIMiddleware(flask_app))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:fastapi_app", host="0.0.0.0", port=5000, reload=True)
