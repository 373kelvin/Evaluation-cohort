---
name: b4-fastapi-greenfield
description: B4 evaluation task — FastAPI transactions service with POST/GET transactions, GET balance, validation, tests. Use when asked about B4 or greenfield FastAPI in evaluation 2.0.
---

# B4 FastAPI Greenfield Agent

## Project
`fastapi_transactions/`

## Required
- POST `/transactions`, GET `/transactions`, GET `/balance`
- Pydantic validation (422 on bad input)
- ≥3 tests in `tests/test_main.py`
- README with install/run/test

## Verify
```bash
cd fastapi_transactions && pytest tests/ -v && uvicorn app.main:app --port 8000
```

Prompt: `agents/b4-fastapi-greenfield/PROMPT.md`
