# Polyglot Fraud-Score Mini-System

A transaction flows through **three languages**: a **FastAPI** service (Python)
ingests it and acts as an in-memory message bus, a **Node.js worker** picks it
up, a **Rust CLI** computes a risk score, and the score is stored back.
No external infra (no DB/Redis) — the service holds state in memory over HTTP.
Amounts are in **Indian Rupees (Rs. / INR)**.

```
client ──POST /transactions──▶ FastAPI service ──(pending list)──▶ Node worker
                                     ▲                                  │
                                     │                          spawn Rust engine
                          POST /{id}/score                       (JSON via stdio)
                                     │                                  │
                                     └──────────── score ◀──────────────┘
```

## Repository layout

```
fraud-score-system/
├── engine/        # Rust scoring CLI (stdin -> stdout)
├── service/       # FastAPI ingestion + bus (in-memory)
├── worker/        # Node.js poller (service <-> engine)
├── integration/   # automated end-to-end test
├── run.sh         # one-shot end-to-end demo + assertion
└── README.md      # this file (the data contract is the spec below)
```

## Shared data contract (the spec — all three components honor this)

**Transaction** (created by ingestion):

```json
{ "id": 1, "amount": 12000.0, "currency": "INR", "hour": 3, "country": "RU", "status": "pending" }
```

- `amount` > 0, `currency` non-empty, `hour` 0–23, `country` a 2-letter code
  (normalized to uppercase). `status` is `pending` | `scored`, server-managed.

**Score** (produced by Rust, submitted by the worker):

```json
{ "score": 90, "reasons": ["large amount", "unusual hour", "high-risk country"] }
```

- `score` is an integer 0–100.

### Scoring rules

| Condition | Points | Reason |
|-----------|-------|--------|
| `amount > 10000` (Rs.) | +40 | large amount |
| `hour` 0–4 | +20 | unusual hour |
| `country` not in `[IN, US, GB]` | +30 | high-risk country |

Example: Rs. 12,000 at 03:00 from RU → 40 + 20 + 30 = **90**.

## Run order

Three terminals (or use `./run.sh` to do it all automatically):

```bash
# 1. Build the Rust engine
cd engine && cargo build --release && cd ..

# 2. Start the service
cd service
pip install -r requirements.txt
uvicorn app.main:app --port 8000
# (leave running; new terminal for the next steps)

# 3. Start the worker (point it at the release binary)
cd worker
SERVICE_URL=http://127.0.0.1:8000 \
ENGINE_BIN=../engine/target/release/engine \
node worker.js

# 4. Post a transaction
curl -X POST http://127.0.0.1:8000/transactions \
  -H 'Content-Type: application/json' \
  -d '{"amount":12000,"currency":"INR","hour":3,"country":"RU"}'

# 5. After ~1s, check it
curl http://127.0.0.1:8000/transactions/1
# -> status "scored", score 90, reasons [...]
```

## Tests

```bash
cd engine && cargo test                 # Rust: 4 tests
cd service && pytest -q                  # FastAPI: 4 tests
pytest -q integration/test_integration.py   # end-to-end (needs engine built)
```

## Requirements

Rust (stable, `cargo`), Python 3.10+ (`fastapi`, `uvicorn`, `pytest`, `httpx`),
Node 18+ (uses the built-in global `fetch` — no npm install needed).
