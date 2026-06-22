"""Evaluation 2.0 — Command Center Dashboard API."""
from __future__ import annotations

import json
import os
import re
import subprocess
import time
from pathlib import Path
from typing import Any

import sys
import httpx
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent.parent
STATIC = Path(__file__).resolve().parent / "static"
OUTPUTS = ROOT / "outputs"
_DASH = Path(__file__).resolve().parent
if str(_DASH) not in sys.path:
    sys.path.insert(0, str(_DASH))
from service_urls import base_url, deployment_config, health_url as svc_health_url, open_buttons, resolve_open_url
from ai_chat import chat, narrate_demo_results, narrate_demo_start
from demo_tests import run_demo_tests
from project_guides import PROJECT_GUIDES
from scan_remote import GitHubDownloadError, download_github_zip, normalize_github_url, save_uploaded_zip, run_insight_scan
from build_info import build_info
from activity_log import check_password, record as dev_record, recent as dev_recent

app = FastAPI(title="Evaluation 2.0 Command Center", version=build_info()["version"])
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.middleware("http")
async def dev_activity_middleware(request: Request, call_next):
    path = request.url.path
    if path.startswith("/api/") and path not in ("/api/build-info", "/api/ping"):
        t0 = time.time()
        response = await call_next(request)
        ms = round((time.time() - t0) * 1000)
        dev_record(
            "api",
            f"{request.method} {path}",
            {"status": response.status_code, "ms": ms},
        )
        return response
    return await call_next(request)

TASKS = [
    {"id": "B1", "name": "Repo Inventory", "agent": "B1 Repo Inventory Agent", "output": "outputs/b1-artifact-inventory/"},
    {"id": "B2", "name": "API Endpoints", "agent": "B2 API Endpoint Agent", "output": "outputs/b2-endpoint-map/"},
    {"id": "B3", "name": "Test Discovery", "agent": "B3 Test Discovery Agent", "output": "outputs/b3-test-results/"},
    {"id": "B4", "name": "FastAPI Greenfield", "agent": "B4 FastAPI Greenfield Agent", "output": "fastapi_transactions/"},
    {"id": "A1", "name": "Parallel Plan", "agent": "A1 Parallel Plan Agent", "output": "outputs/a1-parallel-plan/"},
    {"id": "A2", "name": "Worktree Execute", "agent": "A2 Worktree Execute Agent", "output": "outputs/a2-worktrees/"},
    {"id": "A3", "name": "Polyglot System", "agent": "A3 Polyglot System Agent", "output": "fraud-score-system/"},
    {"id": "A4", "name": "Modernization", "agent": "A4 Modernization Agent", "output": "outputs/a4-modernization/"},
    {"id": "A5", "name": "Code Review", "agent": "A5 Code Review Agent", "output": "outputs/a5-code-review/"},
    {"id": "A6", "name": "Performance", "agent": "A6 Performance Agent", "output": "outputs/a6-performance/"},
]

PROJECTS = [
    {
        "id": "entity-diagrams",
        "name": "Project Insight",
        "subtitle": "B1 / B2 — Repo analyzer",
        "path": "Project-based-entity-diagrams",
        "tasks": ["B1", "B2"],
        "color": "#a78bfa",
        "icon": "🔍",
        "health_url": None,
        "kind": "cli",
    },
    {
        "id": "fastapi-tx",
        "name": "Transactions Service",
        "subtitle": "B4 — FastAPI greenfield",
        "path": "fastapi_transactions",
        "tasks": ["B4", "B3"],
        "color": "#34d399",
        "icon": "💳",
        "health_url": svc_health_url("fastapi-tx"),
    },
    {
        "id": "fraud-score",
        "name": "Fraud Score System",
        "subtitle": "A3 — Python + Node + Rust",
        "path": "fraud-score-system",
        "tasks": ["A3", "B3"],
        "color": "#f472b6",
        "icon": "🛡️",
        "health_url": svc_health_url("fraud-score"),
    },
    {
        "id": "fintech-demo",
        "name": "Fintech Platform",
        "subtitle": "B1 / B2 — Rich scan demo",
        "path": "sample-projects/fintech-platform",
        "tasks": ["B1", "B2"],
        "color": "#38bdf8",
        "icon": "🏦",
        "health_url": svc_health_url("fintech-demo"),
        "featured": True,
    },
]

PROJECTS_BY_ID = {p["id"]: p for p in PROJECTS}


def _dir_has_files(rel: str) -> bool:
    p = ROOT / rel
    if not p.exists():
        return False
    if p.is_file():
        return p.stat().st_size > 50
    return any(p.rglob("*")) if p.is_dir() else False


def _task_status(task: dict) -> str:
    out = ROOT / task["output"]
    if not out.exists():
        return "pending"
    if out.is_dir():
        files = [f for f in out.rglob("*") if f.is_file() and f.name != ".gitkeep"]
        if not files:
            return "pending"
        for f in files:
            if f.stat().st_size > 100:
                return "complete"
        return "partial"
    return "complete" if out.stat().st_size > 100 else "partial"


def _check_url(url: str | None, timeout: float = 0.8) -> dict:
    if not url:
        return {"online": False, "latency_ms": None, "detail": "no health endpoint"}
    t0 = time.perf_counter()
    try:
        r = httpx.get(url, timeout=timeout)
        ms = round((time.perf_counter() - t0) * 1000, 1)
        detail = r.text[:120]
        if r.headers.get("content-type", "").startswith("application/json"):
            try:
                detail = r.json()
            except Exception:
                pass
        return {"online": r.status_code < 500, "latency_ms": ms, "detail": detail}
    except Exception as e:
        return {"online": False, "latency_ms": None, "detail": str(e)[:80]}


def _check_cli_ready(project_id: str) -> dict:
    """Verify CLI scanner scripts exist and Python can invoke them."""
    if project_id != "entity-diagrams":
        return _check_url(PROJECTS_BY_ID.get(project_id, {}).get("health_url"))
    analyze = ROOT / "Project-based-entity-diagrams" / "analyze.py"
    inventory = ROOT / "Project-based-entity-diagrams" / "inventory.py"
    if analyze.is_file() and inventory.is_file():
        try:
            r = subprocess.run(
                ["python3", str(analyze), "--help"],
                capture_output=True, text=True, timeout=3, cwd=ROOT,
            )
            ok = r.returncode == 0
        except Exception:
            ok = analyze.is_file()
        return {
            "online": ok,
            "kind": "cli",
            "latency_ms": None,
            "detail": "Scanner ready — click Run Scan below" if ok else "Scripts missing",
        }
    return {"online": False, "kind": "cli", "latency_ms": None, "detail": "Scripts not found"}


def _project_row(p: dict, health: dict | None = None) -> dict:
    row = {**p, "exists": (ROOT / p["path"]).is_dir()}
    row["health"] = health if health is not None else {"online": False, "latency_ms": None, "detail": "not checked"}
    return row


def _capability_checks(project_id: str) -> list[dict]:
    p = PROJECTS_BY_ID[project_id]
    health = _check_cli_ready(project_id)
    checks: list[dict] = [
        {
            "name": "Project folder present",
            "status": "ok" if (ROOT / p["path"]).exists() else "fail",
            "detail": p["path"],
        }
    ]
    if p.get("kind") == "cli":
        checks.extend(
            [
                {
                    "name": "Scanner scripts available",
                    "status": "ok" if health.get("online") else "fail",
                    "detail": health.get("detail", ""),
                },
                {
                    "name": "Run actions from dashboard",
                    "status": "ok",
                    "detail": "Use B1 Scan / B2 Map buttons.",
                },
            ]
        )
    else:
        checks.extend(
            [
                {
                    "name": "Service health",
                    "status": "ok" if health.get("online") else "warn",
                    "detail": health.get("detail", "not reachable"),
                },
                {
                    "name": "API docs reachable",
                    "status": "ok" if health.get("online") else "warn",
                    "detail": (p.get("health_url") or "").replace("/health", "/docs"),
                },
                {
                    "name": "Tests available",
                    "status": "ok",
                    "detail": "Run 'Run All Tests (B3)' from dashboard.",
                },
            ]
        )
    return checks


def _run(cmd: list[str], cwd: Path | None = None, timeout: int = 120) -> dict:
    try:
        proc = subprocess.run(cmd, cwd=cwd or ROOT, capture_output=True, text=True, timeout=timeout)
        return {"ok": proc.returncode == 0, "code": proc.returncode, "stdout": proc.stdout[-4000:], "stderr": proc.stderr[-2000:]}
    except subprocess.TimeoutExpired:
        return {"ok": False, "code": -1, "stdout": "", "stderr": "timeout"}
    except Exception as e:
        return {"ok": False, "code": -1, "stdout": "", "stderr": str(e)}


def _serve_html(filename: str) -> HTMLResponse:
    """Inject build stamp into static HTML so version shows even before JS runs."""
    path = STATIC / filename
    if not path.is_file():
        raise HTTPException(404, "page not found")
    info = build_info()
    html = path.read_text(encoding="utf-8")
    html = html.replace("__BUILD_DISPLAY__", info["display"])
    html = html.replace("__BUILD_FULL__", info["full"])
    html = html.replace("__BUILD_VERSION__", info["version"])
    v = info["version"]
    for name in ("open-links.js", "project.js", "app.js"):
        html = html.replace(f'/static/{name}"', f'/static/{name}?v={v}"')
    return HTMLResponse(html)


@app.get("/room/{project_id}")
def project_room(project_id: str) -> HTMLResponse:
    if project_id not in PROJECTS_BY_ID:
        raise HTTPException(404, "project not found")
    return _serve_html("project.html")


@app.get("/api/project/{project_id}")
def project_detail(project_id: str) -> dict:
    if project_id not in PROJECTS_BY_ID:
        raise HTTPException(404, "project not found")
    p = PROJECTS_BY_ID[project_id]
    guide = PROJECT_GUIDES.get(project_id, {})
    health = _check_cli_ready(project_id)
    report = OUTPUTS / "b2-endpoint-map" / f"{project_id}-insight.html"
    return {
        "project": _project_row(p, health),
        "guide": guide,
        "open_links": open_buttons(project_id),
        "live_ready": bool(health.get("online")) if p.get("kind") != "cli" else True,
        "has_report": report.is_file(),
        "report_url": f"/api/reports/{project_id}" if report.is_file() else None,
        "tasks": [{**t, "status": _task_status(t)} for t in TASKS if t["id"] in p.get("tasks", [])],
    }


@app.get("/api/config")
def get_config() -> dict:
    """URLs + deploy mode — swap env vars when you deploy, no code change."""
    return deployment_config()


@app.get("/api/build-info")
def get_build_info() -> dict:
    """Public build stamp shown in the corner badge."""
    return build_info()


@app.get("/api/dev/activity")
def dev_activity(request: Request) -> dict:
    """Password-protected server-side activity log (header X-Dev-Pass)."""
    pwd = request.headers.get("X-Dev-Pass", "")
    if not check_password(pwd):
        raise HTTPException(403, "dev log locked")
    return {"events": dev_recent(500), "build": build_info()}


def _open_target_or_503(project_id: str, target: str) -> str:
    """Resolve live URL after health-check; raises HTTPException 503 if offline."""
    if project_id not in PROJECTS_BY_ID:
        raise HTTPException(404, "project not found")
    url = resolve_open_url(project_id, target)
    if not url:
        raise HTTPException(404, "unknown open target")
    h = _check_url(svc_health_url(project_id))
    if not h.get("online"):
        cfg = deployment_config()["services"].get(project_id, {})
        raise HTTPException(
            503,
            detail={
                "message": f"{cfg.get('label', project_id)} is not running. Start it first, then click Open again.",
                "start_cmd": cfg.get("start_cmd", ""),
            },
        )
    return url


@app.get("/api/open-url/{project_id}/{target}")
def open_url_json(project_id: str, target: str) -> dict:
    """Return resolved live URL as JSON — avoids browser redirect/CORS issues."""
    return {"url": _open_target_or_503(project_id, target), "online": True}


@app.get("/api/open/{project_id}/{target}")
def open_service(project_id: str, target: str):
    """Open live app/docs — redirects browser, no localhost shown in UI."""
    return RedirectResponse(_open_target_or_503(project_id, target), status_code=302)


@app.get("/api/capabilities/{project_id}")
def project_capabilities(project_id: str) -> dict:
    if project_id not in PROJECTS_BY_ID:
        raise HTTPException(404, "project not found")
    p = PROJECTS_BY_ID[project_id]
    guide = PROJECT_GUIDES.get(project_id, {})
    health = _check_cli_ready(project_id)
    return {
        "project": _project_row(p, health),
        "capabilities": _capability_checks(project_id),
        "agent_intro": {
            "name": guide.get("agent_name", "Agent"),
            "role": guide.get("agent_role", ""),
            "greeting": guide.get("greeting", ""),
        },
        "actions": guide.get("links", []),
    }


@app.get("/")
def index() -> HTMLResponse:
    return _serve_html("index.html")


@app.get("/api/overview")
def overview() -> dict[str, Any]:
    tasks = [{**t, "status": _task_status(t)} for t in TASKS]
    complete = sum(1 for t in tasks if t["status"] == "complete")
    # Fast response — health checks run separately via /api/projects/health
    projects = [_project_row(p) for p in PROJECTS]
    return {
        "tasks": tasks,
        "projects": projects,
        "summary": {"total_tasks": len(tasks), "complete": complete, "progress_pct": round(100 * complete / len(tasks))},
        "agents_path": "agents/",
        "outputs_path": "outputs/",
    }


@app.get("/api/projects/health")
def projects_health() -> dict:
    results = {}
    for p in PROJECTS:
        try:
            results[p["id"]] = _check_cli_ready(p["id"])
        except Exception:
            results[p["id"]] = {"online": False, "latency_ms": None, "detail": "check failed"}
    return {"health": results}


@app.get("/api/ping")
def ping() -> dict:
    return {"ok": True}


@app.post("/api/demo-tests/{project_id}")
def demo_tests(project_id: str) -> dict:
    if project_id not in PROJECTS_BY_ID:
        raise HTTPException(404, "project not found")
    dev_record("action", "demo_tests", {"project": project_id})
    return run_demo_tests(project_id)


@app.post("/api/chat/{project_id}")
async def ai_chat(project_id: str, request: Request) -> dict:
    if project_id not in PROJECTS_BY_ID:
        raise HTTPException(404, "project not found")
    body = await request.json()
    health = {project_id: _check_cli_ready(project_id)}
    result = chat(project_id, body.get("message", ""), body.get("agent", "master"))
    # Attach live status truth to server responses
    h = health[project_id]
    guide = PROJECT_GUIDES.get(project_id, {})
    if body.get("message", "").lower() and any(w in body.get("message", "").lower() for w in ("running", "online", "live", "status", "open", "link", "work")):
        if project_id == "entity-diagrams" or h.get("kind") == "cli":
            result["reply"] = f"**Status:** Scanner ready.\n\n{result['reply']}"
        elif h.get("online"):
            result["reply"] = f"**Status:** Service online ({h.get('latency_ms')}ms).\n\n{result['reply']}"
        elif guide.get("start_cmd"):
            result["reply"] = f"**Status:** Service not running. Start with: `{guide['start_cmd']}`\n\n{result['reply']}"
    result["live"] = h
    return result


@app.post("/api/chat/{project_id}/demo-start")
def ai_demo_start(project_id: str) -> dict:
    if project_id not in PROJECTS_BY_ID:
        raise HTTPException(404, "project not found")
    return narrate_demo_start(project_id)


@app.post("/api/chat/{project_id}/demo-results")
async def ai_demo_results(project_id: str, request: Request) -> dict:
    if project_id not in PROJECTS_BY_ID:
        raise HTTPException(404, "project not found")
    body = await request.json()
    return narrate_demo_results(project_id, body)


@app.post("/api/actions/run-tests")
def run_tests() -> dict:
    script = ROOT / "scripts" / "run_all_tests.sh"
    if not script.exists():
        raise HTTPException(404, "run_all_tests.sh not found")
    result = _run(["bash", str(script)], timeout=180)
    log = OUTPUTS / "b3-test-results" / "test-run.log"
    tail = log.read_text()[-3000:] if log.exists() else result["stdout"]
    return {"action": "run-tests", "task": "B3", **result, "log_tail": tail}


@app.post("/api/actions/inventory/{project_key}")
def run_inventory(project_key: str) -> dict:
    mapping = {
        "entity-diagrams": ".",
        "fastapi-tx": "fastapi_transactions",
        "fraud-score": "fraud-score-system",
        "fintech-demo": "sample-projects/fintech-platform",
    }
    target = mapping.get(project_key)
    if not target:
        raise HTTPException(404, "unknown project")
    out = OUTPUTS / "b1-artifact-inventory" / f"{project_key}-inventory.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    script = ROOT / "Project-based-entity-diagrams" / "inventory.py"
    result = _run(["python3", str(script), target, "-o", str(out)])
    content = out.read_text()[:2000] if out.exists() else ""
    return {"action": "inventory", "task": "B1", "output": str(out.relative_to(ROOT)), **result, "preview": content}


@app.post("/api/actions/analyze/{project_key}")
def run_analyze(project_key: str) -> dict:
    mapping = {
        "entity-diagrams": "Project-based-entity-diagrams",
        "fastapi-tx": "fastapi_transactions",
        "fraud-score": "fraud-score-system/service",
        "fintech-demo": "sample-projects/fintech-platform",
    }
    target = mapping.get(project_key)
    if not target:
        raise HTTPException(404, "unknown project")
    out = OUTPUTS / "b2-endpoint-map" / f"{project_key}-insight.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    script = ROOT / "Project-based-entity-diagrams" / "analyze.py"
    result = _run(["python3", str(script), target, "-o", str(out)])
    return {"action": "analyze", "task": "B2", "output": str(out.relative_to(ROOT)), "report_url": f"/api/reports/{project_key}", **result}


@app.get("/api/reports")
def list_reports() -> dict:
    """All generated HTML insight reports."""
    reports = []
    report_dir = OUTPUTS / "b2-endpoint-map"
    if report_dir.is_dir():
        for f in sorted(report_dir.glob("*-insight.html"), key=lambda p: p.stat().st_mtime, reverse=True):
            reports.append({
                "id": f.stem.replace("-insight", ""),
                "name": f.stem.replace("-insight", "").replace("-", " ").title(),
                "url": f"/api/reports/{f.stem.replace('-insight', '')}",
                "size_kb": round(f.stat().st_size / 1024, 1),
                "updated": f.stat().st_mtime,
            })
    return {"reports": reports}


@app.post("/api/actions/scan-github")
async def scan_github_repo(request: Request) -> dict:
    """Download a public GitHub repo as zip and run Project Insight (B1 + B2)."""
    body = await request.json()
    url = (body.get("url") or "").strip()
    if not url:
        raise HTTPException(400, "GitHub URL required")
    try:
        url = normalize_github_url(url)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    zip_path = OUTPUTS / "uploads" / f"scan-{int(time.time())}.zip"
    try:
        zip_path, slug, branch = download_github_zip(url, zip_path)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    except GitHubDownloadError as e:
        dev_record("scan", "github_download_fail", {"url": url, "error": str(e)[:200]})
        return {
            "ok": False,
            "source": url,
            "task": "B1+B2",
            "summary": str(e),
            "stderr": str(e),
            "steps": [
                {"label": "Download from GitHub", "status": "fail", "detail": str(e)[:200]},
            ],
        }
    dl_kb = round(zip_path.stat().st_size / 1024, 1)
    result = run_insight_scan(zip_path, slug, source_label=url)
    result["steps"] = [{
        "label": "Download from GitHub",
        "status": "pass",
        "detail": f"branch {branch} · {dl_kb} KB",
    }] + result.get("steps", [])
    result["source"] = url
    result["task"] = "B1+B2"
    result["branch"] = branch
    dev_record("scan", "github_ok", {"url": url, "slug": slug, "branch": branch, "ok": result.get("ok")})
    return result


@app.post("/api/actions/scan-upload")
async def scan_upload_zip(file: UploadFile = File(...)) -> dict:
    """Upload a .zip of any project and run Project Insight (B1 + B2)."""
    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(400, "Upload a .zip file (GitHub Code → Download ZIP works too)")
    content = await file.read()
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(413, "Zip too large (max 50 MB)")
    path = save_uploaded_zip(content, file.filename)
    slug = "upload-" + re.sub(r"[^\w\-]", "-", Path(file.filename).stem)[:40]
    result = run_insight_scan(path, slug, source_label=file.filename)
    result["source"] = file.filename
    result["task"] = "B1+B2"
    result["upload_kb"] = round(len(content) / 1024, 1)
    dev_record("scan", "zip_upload", {"file": file.filename, "kb": result["upload_kb"], "ok": result.get("ok")})
    return result


@app.get("/api/outputs")
def list_outputs() -> dict:
    items = []
    if OUTPUTS.exists():
        for f in sorted(OUTPUTS.rglob("*")):
            if f.is_file() and not f.name.startswith("."):
                items.append({"path": str(f.relative_to(ROOT)), "size": f.stat().st_size})
    return {"outputs": items}


@app.get("/api/reports/{name}")
def get_report(name: str) -> FileResponse:
    safe = name.replace("..", "").replace("/", "")
    candidates = [
        OUTPUTS / "b2-endpoint-map" / f"{safe}-insight.html",
        OUTPUTS / "b2-endpoint-map" / safe,
    ]
    for p in candidates:
        if p.is_file():
            return FileResponse(p)
    raise HTTPException(
        404,
        detail={"message": "No report yet — run a scan first (B2 or GitHub / ZIP upload on Project Insight)."},
    )


@app.get("/api/logs/recent")
def recent_logs() -> dict:
    logs = []
    for name in ("b3-test-results/test-run.log", "b3-test-results/RESULTS.md"):
        p = OUTPUTS / name
        if p.exists():
            logs.append({"name": name, "content": p.read_text()[-2500:]})
    return {"logs": logs}
