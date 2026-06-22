# Transactions Service

A small FastAPI service for recording credit/debit transactions and
tracking a running balance. Built as a self-contained greenfield exercise
(see `B4` in the team's coding-agent eval doc).

## What it does

- `POST /transactions` — create a transaction (`amount`, `type`: `credit`/`debit`, optional `description`). Rejects non-positive amounts and invalid types with `422`.
- `GET /transactions` — list all transactions.
- `GET /transactions/{id}` — fetch a single transaction (`404` if missing).
- `GET /balance` — current balance (sum of credits minus debits) and transaction count.
- `GET /health` — basic liveness check.

Data is stored in memory (a simple list, guarded by a lock), so it resets
whenever the server restarts. That's intentional for this exercise — swap
in a real DB (e.g. Postgres/Redshift) layer if you want persistence.

## Install

```bash
python3 -m venv venv
source venv/bin/activate          # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

The interactive API docs are then available at `http://127.0.0.1:8000/docs`.

### Example usage

```bash
curl -X POST http://127.0.0.1:8000/transactions \
  -H "Content-Type: application/json" \
  -d '{"amount": 200, "type": "credit", "description": "Salary"}'

curl http://127.0.0.1:8000/balance
curl http://127.0.0.1:8000/transactions
```

## Test

```bash
pytest tests/ -v
```

8 tests covering: health check, empty list, credit/debit creation, balance
calculation across multiple transactions, validation rejection (non-positive
amount, invalid type), single-transaction fetch, and 404 handling.

## Project layout

```
app/
  __init__.py
  main.py      # routes
  models.py    # Pydantic schemas + validation
tests/
  __init__.py
  test_main.py
requirements.txt
README.md
```
