# Evaluation 2.0 — AI Agent Workspace

This folder is the **self-contained Evaluation 2.0 submission**. Each evaluation
task (B1–B4, A1–A6) has a dedicated **AI agent** with a Cursor skill, a prompt,
and a project or output folder. The parent repo (`Evaluation-cohort/`) is
reference-only — **all work happens here**.

---

## How it works

```
evaluation 2.0/
├── AGENTS.md                 ← start here: which agent for which task
├── .cursor/skills/           ← Cursor agent skills (auto-loaded in this folder)
├── agents/                   ← copy-paste prompts per task
├── outputs/                  ← agent deliverables (inventory, test logs, plans)
├── scripts/                  ← run tests, generate reports
├── Project-based-entity-diagrams/   ← B1 + B2 agent project
├── fastapi_transactions/            ← B4 agent project
├── fraud-score-system/              ← A3 agent project (+ B3 tests)
└── dashboard/                       ← Command Center UI (monitor all projects + agents)
```

**Launch the dashboard:**
```bash
cd dashboard && pip install -r requirements.txt && uvicorn app:app --port 9000
# → http://127.0.0.1:9000
```

**To run an agent:** open this folder in Cursor, read `AGENTS.md`, then either:
- mention the task (e.g. "run B4 agent") so the matching skill activates, or
- copy the prompt from `agents/<task>/PROMPT.md` into a new Agent chat.

---

## Task → agent → project map

| Task | Agent | Project / output | Time budget |
|------|-------|------------------|-------------|
| **B1** | Repo Inventory Agent | `Project-based-entity-diagrams/` → `outputs/b1-artifact-inventory/` | 30 min |
| **B2** | API Endpoint Agent | same tool → `outputs/b2-endpoint-map/` | 30 min |
| **B3** | Test Discovery Agent | `scripts/run_all_tests.sh` → `outputs/b3-test-results/` | 15 min |
| **B4** | FastAPI Greenfield Agent | `fastapi_transactions/` | 60 min |
| **A1** | Parallel Plan Agent | `outputs/a1-parallel-plan/` | 45 min |
| **A2** | Worktree Execute Agent | `outputs/a2-worktrees/` | 90 min |
| **A3** | Polyglot System Agent | `fraud-score-system/` | 150 min |
| **A4** | Modernization Agent | `outputs/a4-modernization/` | 90 min |
| **A5** | Code Review Agent | `outputs/a5-code-review/` | 60 min |
| **A6** | Performance Agent | `outputs/a6-performance/` | 90 min |

---

## Quick verification (evaluator)

```bash
cd "evaluation 2.0"

# ★ Launch Command Center (recommended first step)
cd dashboard && pip install -r requirements.txt && uvicorn app:app --port 9000
# → http://127.0.0.1:9000  (Three.js UI · dark/light toggle · live scans)

# B1 — artifact inventory markdown
python Project-based-entity-diagrams/inventory.py sample-projects/fintech-platform

# B2 — endpoint HTML report (12 routes · 5 DB tables on fintech demo)
python Project-based-entity-diagrams/analyze.py sample-projects/fintech-platform -o outputs/b2-endpoint-map/fintech-demo-insight.html

# B3 — all tests with saved output
./scripts/run_all_tests.sh

# B4 — greenfield FastAPI (8 tests)
cd fastapi_transactions && pip install -r requirements.txt && pytest tests/ -v

# A3 — polyglot system
cd fraud-score-system && ./run.sh
```

## Sample project for impressive scans

`sample-projects/fintech-platform/` — multi-layer fintech API (FastAPI + Express + MySQL DDL).
Scan results: **27 artifacts · 12 endpoints · 5 tables · 4 FKs**.

---

## Requirements

Python 3.10+, Node 18+, Rust stable (`cargo`), pytest, fastapi, uvicorn.

See each project README for install details.
