#!/usr/bin/env python3
"""Benchmark Project Insight on 10+ database / backend repos."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCANNER = ROOT / "Project-based-entity-diagrams"
DASH = ROOT / "dashboard"
sys.path.insert(0, str(DASH))

from scan_remote import download_github_zip, normalize_github_url, prepare_scan_root  # noqa: E402

# (label, source path or GitHub URL, expect_min_routes, expect_min_tables, notes)
CASES = [
    ("Local · Fintech demo", str(ROOT / "sample-projects/fintech-platform"), 8, 3, "SQL + FastAPI + Express"),
    ("Local · FastAPI transactions", str(ROOT / "fastapi_transactions"), 5, 0, "FastAPI greenfield, in-memory"),
    ("Local · Fraud score API", str(ROOT / "fraud-score-system/service"), 4, 0, "FastAPI polyglot service"),
    ("GitHub · College-ERP (Django)", "https://github.com/samarth-p/College-ERP.git", 20, 10, "Django ORM + urlpatterns"),
    ("GitHub · Ecommerce DBMS", "https://github.com/Saurabh-pec/Ecommerce-Management-DBMS_Project-.git", 10, 3, "React + json-server + README entities"),
    ("GitHub · MERN shift manager", "https://github.com/wiseweb-works/mern-employee-shift-manager.git", 8, 0, "Express + Mongo-style MERN"),
    ("GitHub · FastAPI full-stack template", "https://github.com/tiangolo/full-stack-fastapi-template.git", 15, 1, "FastAPI + SQLAlchemy + React"),
    ("GitHub · Flask SQLAlchemy app", "https://github.com/maxcountryman/flask-login.git", 3, 0, "Flask auth library"),
    ("GitHub · Django allauth", "https://github.com/pennersr/django-allauth.git", 50, 5, "Large Django app with ORM + routes"),
    ("GitHub · Node shopping cart", "https://github.com/ivan3123708/fullstack-shopping-cart.git", 8, 0, "Express + React MERN cart"),
]


def analyze_path(target: str) -> dict:
    out = Path(tempfile.gettempdir()) / f"bench-{abs(hash(target))}.html"
    proc = subprocess.run(
        ["python3", str(SCANNER / "analyze.py"), target, "-o", str(out)],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=SCANNER,
    )
    info = {"ok": proc.returncode == 0, "stdout": proc.stdout, "stderr": proc.stderr[-400:] if proc.stderr else ""}
    for line in (proc.stdout or "").splitlines():
        if "features:" in line:
            info["features"] = int(line.split("features:")[-1].strip())
        if "tables:" in line:
            part = line.split("tables:")[-1].strip().split()[0]
            info["tables"] = int(part)
        if "files:" in line:
            info["files"] = int(line.split("files:")[-1].strip())
        if "stack:" in line:
            info["stack"] = line.split("stack:")[-1].strip()
        if "verdict:" in line:
            info["verdict"] = line.split("verdict:")[-1].strip()
    info.setdefault("features", 0)
    info.setdefault("tables", 0)
    info.setdefault("files", 0)
    return info


def resolve_target(source: str) -> tuple[str, tempfile.TemporaryDirectory | None]:
    if source.startswith("http"):
        url = normalize_github_url(source)
        z = Path(tempfile.gettempdir()) / f"bench-{abs(hash(url))}.zip"
        path, _, _ = download_github_zip(url, z)
        root, tmp = prepare_scan_root(path)
        return str(root), tmp
    return source, None


def main() -> int:
    results = []
    print(f"{'Project':<42} {'Routes':>6} {'Tables':>6} {'Files':>6}  Pass  Notes")
    print("-" * 95)
    for label, source, min_r, min_t, notes in CASES:
        tmp = None
        try:
            target, tmp = resolve_target(source)
            r = analyze_path(target)
            pass_r = r["features"] >= min_r
            pass_t = r["tables"] >= min_t
            ok = r["ok"] and pass_r and pass_t
            status = "✓" if ok else "✗"
            print(f"{label:<42} {r['features']:>6} {r['tables']:>6} {r['files']:>6}  {status:>4}  {notes}")
            if not ok:
                why = []
                if not r["ok"]:
                    why.append("analyze failed")
                if r["features"] < min_r:
                    why.append(f"routes<{min_r}")
                if r["tables"] < min_t:
                    why.append(f"tables<{min_t}")
                print(f"    ↳ {' · '.join(why)} · {r.get('stack', '?')}")
            results.append({
                "label": label,
                "source": source,
                "features": r["features"],
                "tables": r["tables"],
                "files": r["files"],
                "stack": r.get("stack"),
                "verdict": r.get("verdict"),
                "pass": ok,
                "notes": notes,
            })
        except Exception as e:
            print(f"{label:<42} {'—':>6} {'—':>6} {'—':>6}  ✗    ERROR: {e}")
            results.append({"label": label, "source": source, "pass": False, "error": str(e)})
        finally:
            if tmp is not None:
                tmp.cleanup()

    passed = sum(1 for x in results if x.get("pass"))
    print("-" * 95)
    print(f"Passed {passed}/{len(CASES)}")
    out_json = ROOT / "outputs" / "b3-test-results" / "scan-benchmark.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {out_json}")
    return 0 if passed >= len(CASES) * 0.7 else 1


if __name__ == "__main__":
    raise SystemExit(main())
