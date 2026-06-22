---
name: a3-polyglot-system
description: A3 evaluation task — fraud-score system with FastAPI, Node worker, Rust engine. Use when asked about A3 or polyglot mini-system in evaluation 2.0.
---

# A3 Polyglot System Agent

## Project
`fraud-score-system/`

## Components
- `service/app/main.py` — FastAPI ingestion
- `worker/worker.js` — Node poller
- `engine/src/main.rs` — Rust scoring CLI

## Verify
```bash
cd fraud-score-system && ./run.sh
cd service && pytest -q
cd ../engine && cargo test
```

Prompt: `agents/a3-polyglot-system/PROMPT.md`
