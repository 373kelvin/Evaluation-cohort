# Evaluation Cohort — Coding Agent Assessment

This repository is a **submission portfolio** for the coding-agent evaluation track.
It contains working code, tests, and documentation that map directly to the
**Basic (B1–B4)** and **Advanced (A1–A6)** tasks described below.

Each sub-project lives in its own directory with its own README, install/run
instructions, and tests. Use this file as the **evaluator entry point** — it
explains what was built, which task it satisfies, and how to verify it quickly.

---

## Repository map

```
Evaluation-cohort/
├── fastapi_transactions/          # B4 — FastAPI greenfield service
├── fraud-score-system/            # A3 — Polyglot mini-system (Python + Node + Rust)
├── Project-based-entity-diagrams/ # B1 / B2 — Repo inventory & endpoint discovery tool
└── README.md                      # this file
```

---

## Task coverage at a glance

| Task | Title | Status | Where to look |
|------|-------|--------|---------------|
| **B1** | Repo artifact inventory | Tool provided | `Project-based-entity-diagrams/` — run on any repo to surface classes, services, configs, utilities |
| **B2** | API endpoint map | Tool provided | Same tool — detects every route/handler with file:line citations |
| **B3** | Test discovery and execution | Documented below | Test commands and file paths for each sub-project |
| **B4** | FastAPI greenfield service | **Complete** | `fastapi_transactions/` |
| **A1** | Multi-worktree parallel plan | Process task | Not a code artifact — evaluated via agent session output |
| **A2** | Execute two parallel worktrees | Process task | Not a code artifact — evaluated via git worktree evidence |
| **A3** | Polyglot mini-system | **Complete** | `fraud-score-system/` |
| **A4** | Repository modernization plan | Process task | Not a code artifact in this repo |
| **A5** | Agent code review | Process task | Not a code artifact in this repo |
| **A6** | Performance profiling | Process task | Not a code artifact in this repo |

---

## B1 — Repo artifact inventory (30 min)

**Goal:** Find major classes, interfaces, services, controllers, models,
repositories, jobs, consumers, configs, and utilities within 30 minutes.

**Deliverable:** `Project-based-entity-diagrams/` — a static Python analyzer
(stdlib only, no API keys) that scans any codebase and produces an interactive
HTML report covering stack, features, data model, architecture diagrams, and
security findings.

```bash
cd Project-based-entity-diagrams
python analyze.py ../fraud-score-system          # scan the polyglot system
python analyze.py ../fastapi_transactions        # scan the greenfield service
# opens <name>-insight.html with full artifact inventory
```

Key modules: `insight/scan.py`, `insight/stack.py`, `insight/features.py`,
`insight/schema.py`, `insight/design.py`, `insight/render.py`.

See `Project-based-entity-diagrams/README.md` for full details.

---

## B2 — API endpoint map (30 min)

**Goal:** Identify every externally exposed API route or frontend route.

**Deliverable:** Same analyzer — `insight/features.py` detects routes in
Express, Flask, FastAPI, and PHP with file:line citations.

### Endpoints in this repo (manual reference)

**`fastapi_transactions/`** (B4 service):

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | Web UI (static HTML) |
| POST | `/transactions` | Create credit/debit transaction |
| GET | `/transactions` | List all transactions |
| GET | `/transactions/{id}` | Fetch single transaction |
| GET | `/balance` | Current balance + count |
| GET | `/health` | Liveness check |
| GET | `/docs` | Swagger UI (auto-generated) |

**`fraud-score-system/service/`** (A3 ingestion service):

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/transactions` | Ingest transaction (status: pending) |
| GET | `/transactions/pending` | List pending (worker polls this) |
| POST | `/transactions/{id}/score` | Submit score from worker |
| GET | `/transactions/{id}` | Fetch transaction with score |

---

## B3 — Test discovery and execution (15 min)

**Goal:** Find the test framework, relevant test files, exact commands, and results.

### `fastapi_transactions/` — pytest

| Item | Detail |
|------|--------|
| Framework | **pytest** (no separate config file; defaults used) |
| Test files | `fastapi_transactions/tests/test_main.py` |
| Command | `cd fastapi_transactions && pytest tests/ -v` |
| Coverage | 8 tests — health, CRUD, balance, validation (422), 404 |

```bash
cd fastapi_transactions
pip install -r requirements.txt
pytest tests/ -v
# 8 passed
```

### `fraud-score-system/` — pytest + cargo test

| Component | Framework | Test file | Command |
|-----------|-----------|-----------|---------|
| FastAPI service | pytest | `service/tests/test_service.py` | `cd fraud-score-system/service && pytest -q` |
| Rust engine | cargo test | inline in `engine/src/main.rs` | `cd fraud-score-system/engine && cargo test` |
| Integration | pytest | `integration/test_integration.py` | `cd fraud-score-system && pytest -q integration/test_integration.py` |

```bash
# FastAPI unit tests (4 tests)
cd fraud-score-system/service && pip install -r requirements.txt && pytest -q
# 4 passed

# Rust unit tests (4 tests — requires Rust toolchain)
cd fraud-score-system/engine && cargo test
# 4 passed

# End-to-end integration (requires engine built + service running, or run via run.sh)
cd fraud-score-system && ./run.sh
```

---

## B4 — FastAPI greenfield service (1 hour)

**Goal:** Build a small Python FastAPI service from scratch with POST/GET
transactions, GET balance, input validation, ≥3 tests, and a README.

**Deliverable:** `fastapi_transactions/`

| Requirement | Evidence |
|-------------|----------|
| FastAPI app | `app/main.py` |
| POST `/transactions` | Creates credit/debit with Pydantic validation |
| GET `/transactions` | Lists all transactions |
| GET `/balance` | Returns balance and transaction count |
| Input validation | Rejects non-positive amounts and invalid types → 422 |
| ≥3 tests | 8 tests in `tests/test_main.py` |
| README | `fastapi_transactions/README.md` |

```bash
cd fastapi_transactions
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
# API docs: http://127.0.0.1:8000/docs
# Web UI:    http://127.0.0.1:8000/
```

---

## A3 — Polyglot mini-system: FastAPI + Node worker + Rust engine (150 min)

**Goal:** Build a fraud-score system across Python, Node.js, and Rust with a
clear data contract, tests, and README with run order.

**Deliverable:** `fraud-score-system/`

```
client ──POST /transactions──▶ FastAPI service ──(pending list)──▶ Node worker
                                     ▲                                  │
                                     │                          spawn Rust engine
                          POST /{id}/score                       (JSON via stdio)
                                     │                                  │
                                     └──────────── score ◀──────────────┘
```

| Requirement | Location |
|-------------|----------|
| FastAPI ingestion endpoint | `service/app/main.py` |
| Node.js worker process | `worker/worker.js` |
| Rust scoring CLI | `engine/src/main.rs` |
| Data contract | Documented in `fraud-score-system/README.md` |
| Unit tests | Rust (4), FastAPI (4) |
| Integration test | `integration/test_integration.py` |
| One-shot demo | `./run.sh` |

### Scoring rules (Rust engine)

| Condition | Points | Reason |
|-----------|-------|--------|
| `amount > 10000` (Rs.) | +40 | large amount |
| `hour` 0–4 | +20 | unusual hour |
| `country` not in `[IN, US, GB]` | +30 | high-risk country |

Example: Rs. 12,000 at 03:00 from RU → 40 + 20 + 30 = **90**.

### Run order

```bash
cd fraud-score-system

# Option A — automated (builds engine, starts service + worker, posts txn, asserts score)
./run.sh

# Option B — manual (three terminals)
cd engine && cargo build --release && cd ..
cd service && pip install -r requirements.txt && uvicorn app.main:app --port 8000
cd worker && SERVICE_URL=http://127.0.0.1:8000 ENGINE_BIN=../engine/target/release/engine node worker.js
curl -X POST http://127.0.0.1:8000/transactions \
  -H 'Content-Type: application/json' \
  -d '{"amount":12000,"currency":"INR","hour":3,"country":"RU"}'
curl http://127.0.0.1:8000/transactions/1   # status "scored", score 90
```

See `fraud-score-system/README.md` for the full data contract and component docs.

---

## Advanced tasks (A1, A2, A4–A6)

These are **process and judgment tasks** evaluated during the live session,
not as standalone code in this repository:

| Task | What the evaluator should look for |
|------|-------------------------------------|
| **A1** | Task decomposition, worktree/branch plan, agent prompts, merge order |
| **A2** | Git worktree commands, parallel branch outputs, clean merge, test results |
| **A4** | Modernization findings with file evidence, prioritised plan, first step implemented |
| **A5** | Issue list with severity, suggested fixes, verification steps |
| **A6** | Baseline vs after measurements, profiling output, targeted code change |

Evidence for these tasks is provided in the **evaluation session transcript**
and any associated PRs or worktree branches, not in this repo's file tree.

---

## Requirements

| Tool | Version | Used by |
|------|---------|---------|
| Python | 3.10+ | All Python sub-projects |
| pip packages | see each `requirements.txt` | FastAPI services, tests |
| Node.js | 18+ | `fraud-score-system/worker/` (built-in `fetch`, no npm install) |
| Rust | stable (`cargo`) | `fraud-score-system/engine/` |

---

## Quick verification checklist for evaluators

```bash
# 1. B4 — greenfield FastAPI (should pass 8 tests)
cd fastapi_transactions && pip install -r requirements.txt && pytest tests/ -v

# 2. A3 — polyglot system FastAPI layer (should pass 4 tests)
cd fraud-score-system/service && pip install -r requirements.txt && pytest -q

# 3. A3 — Rust engine (should pass 4 tests, requires cargo)
cd fraud-score-system/engine && cargo test

# 4. A3 — full end-to-end demo
cd fraud-score-system && ./run.sh

# 5. B1/B2 — scan this repo itself
cd Project-based-entity-diagrams && python analyze.py ../fraud-score-system
```
