# A1 — Parallel Worktree Plan

> **Task:** Add structured logging to `fraud-score-system` without blocking a parallel metrics endpoint on the FastAPI service.

## 1. Task decomposition

| Lane | Scope | Touches |
|------|-------|---------|
| **Lane A** | Add JSON logging to Node worker + FastAPI service | `worker/worker.js`, `service/app/main.py` |
| **Lane B** | Add `GET /metrics` Prometheus-style counter on FastAPI | `service/app/main.py`, `service/tests/test_service.py` |

No shared files except `service/app/main.py` — merge Lane B after Lane A.

## 2. Worktree / branch names

```bash
git worktree add ../wt-lane-a-logging -b feat/lane-a-logging
git worktree add ../wt-lane-b-metrics -b feat/lane-b-metrics
```

## 3. Agent prompt for each lane

**Lane A — Logging Agent**
```
In worktree wt-lane-a-logging, add structured console.log JSON lines to
worker/worker.js (poll, score, error events) and a logging middleware stub
in service/app/main.py. Do not add new routes. Run pytest in service/.
```

**Lane B — Metrics Agent**
```
In worktree wt-lane-b-metrics, add GET /metrics returning JSON
{transactions_ingested, transactions_scored, pending_count}.
Add one pytest. Do not modify worker/. Run pytest in service/.
```

## 4. Shared constraints

- Data contract (Transaction / Score JSON) must not change
- Lane A merges first; Lane B rebases onto main after A
- Both lanes must pass `cd service && pytest -q` before merge

## 5. Merge order

1. **Lane A** → `main` (logging only, no route conflicts)
2. **Lane B** → rebase on updated `main`, resolve `main.py` if needed
3. Run `./run.sh` after both merged

## 6. Conflict / risk plan

| Risk | Mitigation |
|------|------------|
| Both edit `service/app/main.py` | Sequential merge; B rebases after A |
| Worker env vars change | Lane B forbidden from touching `worker/` |
| Test flakiness | `_reset()` in conftest isolates state |

## 7. Verification plan

```bash
cd fraud-score-system/service && pytest -q          # unit
cd .. && ./run.sh                                    # e2e
curl http://127.0.0.1:8000/metrics                  # Lane B only
```
