# Service — FastAPI ingestion + in-memory bus

## Install & run

```bash
cd service
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Service runs at http://127.0.0.1:8000 (interactive docs at `/docs`).

## Test

```bash
cd service
pytest -q
```

## Endpoints

| Method | Path | Behavior |
|--------|------|----------|
| POST | `/transactions` | validate + store as `pending`, assign id, return it |
| GET | `/transactions/pending` | list all `pending` transactions |
| POST | `/transactions/{id}/score` | attach `{score, reasons}`, set status `scored` |
| GET | `/transactions/{id}` | return the transaction incl. score if scored |

Validation (Pydantic): `amount` > 0, `currency` non-empty, `hour` 0–23,
`country` a 2-letter code (normalized to uppercase). Bad input → 422.

## Quick manual check

```bash
curl -X POST http://127.0.0.1:8000/transactions \
  -H 'Content-Type: application/json' \
  -d '{"amount":12000,"currency":"INR","hour":3,"country":"RU"}'
# -> {"id":1,...,"status":"pending",...}
curl http://127.0.0.1:8000/transactions/pending
```
