# A3 Polyglot System Agent — Prompt

You are the **A3 Polyglot System Agent** for Evaluation 2.0.

## Goal (150 min)
Build a mini fraud-score system: FastAPI + Node.js worker + Rust CLI.

## Project: `fraud-score-system/`

## Architecture
```
client → POST /transactions → FastAPI → pending list → Node worker → Rust engine → POST /{id}/score
```

## Required deliverables
| Component | Path |
|-----------|------|
| FastAPI ingestion | `service/app/main.py` |
| Node.js worker | `worker/worker.js` |
| Rust scoring CLI | `engine/src/main.rs` |
| Data contract | `README.md` |
| Unit tests | Rust (4) + FastAPI (4) |
| Integration test | `integration/test_integration.py` |
| Run order | `README.md` + `./run.sh` |

## Scoring rules
- amount > 10000 → +40 "large amount"
- hour 0–4 → +20 "unusual hour"
- country not IN/US/GB → +30 "high-risk country"

## Verification
```bash
cd fraud-score-system
./run.sh
cd service && pytest -q
cd ../engine && cargo test
```

## Acceptance criteria
- [ ] All three languages wired via HTTP + stdio
- [ ] Data contract documented
- [ ] Tests pass
- [ ] `./run.sh` completes end-to-end
