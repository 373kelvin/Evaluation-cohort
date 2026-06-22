# Worker — Node.js poller

Polls the service for pending transactions, scores each one by spawning the
Rust engine, and posts the score back. Requires **Node 18+** (built-in `fetch`).
No npm dependencies.

## Run

```bash
cd worker
# Defaults: SERVICE_URL=http://127.0.0.1:8000, ENGINE_BIN=../engine/target/release/engine
node worker.js

# Override if your paths differ:
SERVICE_URL=http://127.0.0.1:8000 \
ENGINE_BIN=../engine/target/release/engine \
node worker.js
```

On Windows the binary is `..\engine\target\release\engine.exe`.

## Behavior

- Polls `GET /transactions/pending` every ~1s.
- For each txn: spawns the engine, writes the txn JSON to its stdin, reads the
  Score JSON from stdout, then `POST /transactions/{id}/score`.
- **Engine missing** → logs a clear build hint, skips the txn, keeps running.
- **Service unreachable** → logs and backs off ~3s, does not crash.
