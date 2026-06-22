# B4 FastAPI Greenfield Agent — Prompt

You are the **B4 FastAPI Greenfield Agent** for Evaluation 2.0.

## Goal (60 min)
Build (or verify) a small Python FastAPI service from scratch and prove it runs.

## Project: `fastapi_transactions/`

## Required deliverables
| Requirement | Location |
|-------------|----------|
| FastAPI app | `app/main.py` |
| POST `/transactions` | Create credit/debit transaction |
| GET `/transactions` | List all transactions |
| GET `/balance` | Balance + transaction count |
| Input validation | Pydantic models → 422 on bad input |
| ≥3 tests | `tests/test_main.py` |
| README | install / run / test commands |

## Verification
```bash
cd fastapi_transactions
pip install -r requirements.txt
pytest tests/ -v          # expect 8 passed
uvicorn app.main:app --port 8000
curl http://127.0.0.1:8000/health
```

## Acceptance criteria
- [ ] All routes work
- [ ] ≥3 tests pass (currently 8)
- [ ] README has install, run, test sections
- [ ] Service runs without external DB (in-memory is fine)
