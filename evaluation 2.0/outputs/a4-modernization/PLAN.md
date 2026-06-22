# A4 — Repository Modernization

## 1. Findings (with evidence)

| # | Finding | Evidence | Priority |
|---|---------|----------|----------|
| 1 | No CI pipeline | No `.github/workflows/` in repo | High |
| 2 | Unpinned Python deps | `requirements.txt` uses bare `fastapi` without `==` | Medium |
| 3 | In-memory stores reset on restart | `fastapi_transactions/app/main.py:21-23` | Low (by design) |
| 4 | Analyzer missing Rust route detection | `Project-based-entity-diagrams/insight/features.py` — no Actix/Axum patterns | Medium |
| 5 | Duplicate `__pycache__` in tree | `fastapi_transactions/app/__pycache__/` committed locally | High |
| 6 | No unified eval dashboard | Agents exist but no single monitoring UI | Medium → **addressed** |

## 2. Prioritized plan

1. **Add evaluation dashboard** (high value, low risk) — single UI to monitor all 3 projects
2. Add `.github/workflows/test.yml` for Python pytest on push
3. Pin dependencies with `pip freeze` or `uv lock`
4. Extend analyzer for Rust HTTP frameworks
5. Add optional SQLite persistence behind env flag

## 3. First step implemented

**Dashboard added:** `evaluation 2.0/dashboard/`

- FastAPI server on port **9000**
- Monitors all 3 projects + 10 agent tasks
- Triggers B1/B2/B3 scans from the UI
- Links to output artifacts

## 4. Verification

```bash
cd "evaluation 2.0/dashboard"
pip install -r requirements.txt
uvicorn app:app --port 9000
# Open http://127.0.0.1:9000 — all project cards show status
curl http://127.0.0.1:9000/api/overview
```

## 5. Rollback notes

```bash
rm -rf "evaluation 2.0/dashboard"
# Remove dashboard section from evaluation 2.0/README.md if added
```

No changes to core project logic — safe to remove without affecting B4 or A3.
