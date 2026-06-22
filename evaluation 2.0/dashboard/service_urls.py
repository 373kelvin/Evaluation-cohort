"""Service URL config — localhost now, path-based proxy when deployed (Railway/Docker)."""
from __future__ import annotations

import os

# Override with full public URLs if you split services later:
#   EVAL_TX_URL=https://transactions.example.com
#   EVAL_FRAUD_URL=https://fraud.example.com
#   EVAL_FINTECH_URL=https://fintech.example.com
#
# Docker/Railway (single container): set PUBLIC_BASE_URL or rely on RAILWAY_PUBLIC_DOMAIN.
# Open buttons resolve to:
#   {PUBLIC_BASE_URL}/services/tx
#   {PUBLIC_BASE_URL}/services/fraud
#   {PUBLIC_BASE_URL}/services/fintech

INTERNAL_BASE = {
    "fastapi-tx": "http://127.0.0.1:8000",
    "fraud-score": "http://127.0.0.1:8001",
    "fintech-demo": "http://127.0.0.1:8002",
}

PUBLIC_PATHS = {
    "fastapi-tx": "/services/tx",
    "fraud-score": "/services/fraud",
    "fintech-demo": "/services/fintech",
}

SERVICES = {
    "fastapi-tx": {
        "env_key": "EVAL_TX_URL",
        "default_base": "http://127.0.0.1:8000",
        "label": "Transactions App",
        "start_cmd": "cd fastapi_transactions && uvicorn app.main:app --port 8000",
    },
    "fraud-score": {
        "env_key": "EVAL_FRAUD_URL",
        "default_base": "http://127.0.0.1:8001",
        "label": "Fraud Score API",
        "start_cmd": "cd fraud-score-system/service && uvicorn app.main:app --port 8001",
    },
    "fintech-demo": {
        "env_key": "EVAL_FINTECH_URL",
        "default_base": "http://127.0.0.1:8002",
        "label": "Fintech Platform",
        "start_cmd": "cd sample-projects/fintech-platform && PYTHONPATH=. uvicorn app.main:app --port 8002",
    },
}

OPEN_TARGETS = {
    "web": {"path": "/", "button": "🌐 Open Web App"},
    "docs": {"path": "/docs", "button": "📖 Open API Docs (Swagger)"},
    "app": {"path": "/", "button": "🌐 Open App"},
}


def _base(env_key: str, default: str) -> str:
    return os.environ.get(env_key, default).rstrip("/")


def _public_base() -> str | None:
    explicit = os.environ.get("PUBLIC_BASE_URL", "").strip()
    if explicit:
        return explicit.rstrip("/")
    domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "").strip()
    if domain:
        return f"https://{domain}"
    return None


def internal_base_url(project_id: str) -> str:
    """Server-side health checks and demo tests (inside the container)."""
    return INTERNAL_BASE.get(project_id, "")


def base_url(project_id: str) -> str:
    """Browser-facing URL for Open buttons."""
    pub = _public_base()
    if pub and project_id in PUBLIC_PATHS:
        return pub + PUBLIC_PATHS[project_id]
    cfg = SERVICES.get(project_id)
    if not cfg:
        return ""
    return _base(cfg["env_key"], cfg["default_base"])


def health_url(project_id: str) -> str | None:
    b = internal_base_url(project_id)
    return f"{b}/health" if b else None


def resolve_open_url(project_id: str, target: str) -> str | None:
    if project_id not in SERVICES:
        return None
    meta = OPEN_TARGETS.get(target)
    if not meta:
        return None
    return base_url(project_id) + meta["path"]


def open_buttons(project_id: str) -> list[dict]:
    if project_id == "fastapi-tx":
        return [
            {"target": "web", "label": "🌐 Open Web App", "hint": "Opens the ledger in a new tab"},
            {"target": "docs", "label": "📖 Open API Docs", "hint": "Try endpoints in Swagger UI"},
        ]
    if project_id == "fraud-score":
        return [
            {"target": "docs", "label": "📖 Open API Docs", "hint": "Post a test transaction here"},
        ]
    if project_id == "fintech-demo":
        return [
            {"target": "docs", "label": "📖 Open API Docs", "hint": "Live fintech endpoints"},
        ]
    if project_id == "entity-diagrams":
        return [
            {"target": "report", "label": "📊 Open Scan Report", "hint": "Fintech demo HTML diagram", "href": "/api/reports/fintech-demo"},
        ]
    return []


def deployment_config() -> dict:
    pub = _public_base()
    return {
        "mode": "deployed" if pub or any(os.environ.get(s["env_key"]) for s in SERVICES.values()) else "local",
        "public_base_url": pub,
        "services": {
            pid: {
                "label": s["label"],
                "base_url": base_url(pid),
                "internal_base_url": internal_base_url(pid),
                "health_url": health_url(pid),
                "start_cmd": s["start_cmd"],
            }
            for pid, s in SERVICES.items()
        },
        "deploy_env_vars": ["PUBLIC_BASE_URL", "RAILWAY_PUBLIC_DOMAIN"] + [s["env_key"] for s in SERVICES.values()],
    }
