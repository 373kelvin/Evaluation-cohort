# Evaluation 2.0 Command Center

Premium dashboard for evaluator demos — **Three.js** particle network, **dark/light mode**, live project monitoring.

## One-command demo

```bash
bash "evaluation 2.0/scripts/start_dashboard.sh"
```

The script picks a free port (9010+ on macOS), prints the URL, and tries to open it in your browser.

Or manually:

```bash
cd "evaluation 2.0/dashboard"
pip install -r requirements.txt
uvicorn app:app --host 127.0.0.1 --port 9010
```

### What to show evaluators

1. **Hero + progress ring** — 10/10 agents, completion %
2. **4 project cards** — including **Fintech Platform** (rich B1/B2 scan target)
3. **Open Project Page** → click **Open Web App** / **Open API Docs** (no localhost URLs to copy)
4. **👁 Step-by-Step Demo** — guided walkthrough with **Open now** when a service is live
5. Toggle **☀ / ☾** top-right for dark/light mode

### Optional — show services Online (green dot)

```bash
# Terminal 2 — B4
cd fastapi_transactions && uvicorn app.main:app --port 8000

# Terminal 3 — A3
cd fraud-score-system/service && uvicorn app.main:app --port 8001

# Terminal 4 — Fintech demo
cd sample-projects/fintech-platform && PYTHONPATH=. uvicorn app.main:app --port 8002
```

Refresh dashboard — cards turn **Online**. Open buttons work in one click.

## Deployment-ready URLs (future)

Service URLs are centralized in `service_urls.py`. For production, set env vars — no code changes:

```bash
export EVAL_TX_URL=https://transactions.example.com
export EVAL_FRAUD_URL=https://fraud.example.com
export EVAL_FINTECH_URL=https://fintech.example.com
```

The dashboard exposes `GET /api/config` with `mode: local|deployed` and resolved base URLs.
Open buttons use `GET /api/open/{project}/{target}` (health-check then redirect).

## Tech

- FastAPI backend (`app.py`)
- Three.js animated particle network (`three-scene.js`)
- CSS glassmorphism + theme variables (`styles.css`)
- No build step — static assets served directly
