#!/usr/bin/env bash
# End-to-end demo: build engine, start service + worker, post a transaction,
# verify it becomes `scored`. Run from the fraud-score-system/ directory.
#
#   chmod +x run.sh && ./run.sh
#
# Assumes: cargo, python3 (with service deps installed), node 18+ on PATH.

set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

SERVICE_URL="http://127.0.0.1:8000"
ENGINE_BIN="$HERE/engine/target/release/engine"

cleanup() {
  [[ -n "${WORKER_PID:-}" ]] && kill "$WORKER_PID" 2>/dev/null || true
  [[ -n "${SERVICE_PID:-}" ]] && kill "$SERVICE_PID" 2>/dev/null || true
}
trap cleanup EXIT

echo "==> 1. Build Rust engine"
( cd engine && cargo build --release )

echo "==> 2. Start FastAPI service"
( cd service && uvicorn app.main:app --port 8000 ) &
SERVICE_PID=$!

echo "==> waiting for service..."
for _ in $(seq 1 30); do
  if curl -sf "$SERVICE_URL/transactions/pending" >/dev/null 2>&1; then break; fi
  sleep 0.5
done

echo "==> 3. Start Node worker"
( cd worker && SERVICE_URL="$SERVICE_URL" ENGINE_BIN="$ENGINE_BIN" node worker.js ) &
WORKER_PID=$!

echo "==> 4. Post a transaction"
curl -sf -X POST "$SERVICE_URL/transactions" \
  -H 'Content-Type: application/json' \
  -d '{"amount":12000,"currency":"INR","hour":3,"country":"RU"}'
echo

echo "==> 5. Wait for the worker to score it"
STATUS=""
for _ in $(seq 1 15); do
  sleep 1
  RESP="$(curl -sf "$SERVICE_URL/transactions/1" || true)"
  echo "    $RESP"
  if echo "$RESP" | grep -q '"status":"scored"'; then
    STATUS="scored"
    break
  fi
done

if [[ "$STATUS" == "scored" ]]; then
  echo "==> PASS: transaction 1 is scored."
  exit 0
else
  echo "==> FAIL: transaction 1 never reached scored status."
  exit 1
fi
