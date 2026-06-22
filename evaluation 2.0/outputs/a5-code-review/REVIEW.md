# A5 — Agent Code Review

| # | Severity | Blocking? | File | Issue | Suggested fix | Verification |
|---|----------|-----------|------|-------|---------------|--------------|
| 1 | **High** | Yes | `fraud-score-system/worker/worker.js:26` | `spawn(ENGINE_BIN)` without absolute path validation — path injection if env compromised | Resolve with `path.resolve` and reject `..` segments | Unit test with malicious `ENGINE_BIN` |
| 2 | **Medium** | No | `fastapi_transactions/app/main.py:40` | Dummy seed data runs at import — surprises tests expecting empty store | Move `_seed_dummy_data()` behind env flag `SEED_DEMO=1` | Test empty list without seed |
| 3 | **Medium** | No | `fraud-score-system/service/app/main.py:45` | Global `_transactions` dict not thread-safe under async load | Use `threading.Lock` or async store | Concurrent POST stress test |
| 4 | **Low** | No | `Project-based-entity-diagrams/insight/features.py` | Regex-based parsing may miss `@router.get` multiline decorators | Extend FASTAPI_RE or use AST | Scan FastAPI project, assert ≥7 routes |
| 5 | **Info** | No | `fraud-score-system/engine/src/main.rs:45` | Score clamp to 100 is dead code with current rules (max 90) | Keep as safety net or document | `cargo test` |
| 6 | **Low** | No | `fastapi_transactions/app/models.py:28` | `created_at` uses naive UTC — fine for demo but not timezone-aware display | Use `datetime.now(timezone.utc).isoformat()` consistently | Existing tests pass |

## Summary

- **1 blocking** (worker spawn path validation)
- **3 non-blocking** medium/low
- **2 informational**

Recommended merge gate: fix #1 before production; #2–#6 can be follow-up PRs.
