#!/usr/bin/env bash
# Start Evaluation 2.0 Command Center.
# Picks first bindable port (9000 is often taken or hung on macOS).
# Usage: start_dashboard.sh          — start if not running
#        start_dashboard.sh restart  — kill old server, start fresh (after code changes)
set -euo pipefail
DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$DIR/dashboard"

if [[ "${1:-}" == "restart" ]]; then
  for p in 9000 9010 9020 9030 9040; do
    lsof -ti ":$p" 2>/dev/null | xargs kill -9 2>/dev/null || true
  done
  sleep 1
  echo "[ok] Stopped old dashboard — starting fresh…"
fi

PORT="$(python3 <<'PY'
import json
import socket
import subprocess
import sys
import time

CANDIDATES = [9000, 9010, 9020, 9030, 9040]


def responds(port: int) -> bool:
    try:
        r = subprocess.run(
            ["curl", "-sf", "--max-time", "2", f"http://127.0.0.1:{port}/api/ping"],
            capture_output=True,
            text=True,
        )
        if r.returncode != 0:
            return False
        return json.loads(r.stdout).get("ok") is True
    except Exception:
        return False


def can_bind(port: int) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(("127.0.0.1", port))
        return True
    except OSError:
        return False
    finally:
        s.close()


def clear_port(port: int) -> None:
    try:
        out = subprocess.check_output(["lsof", "-ti", f":{port}"], text=True).strip()
        if out:
            for pid in out.splitlines():
                subprocess.run(["kill", "-9", pid], check=False)
            time.sleep(0.5)
    except subprocess.CalledProcessError:
        pass


for port in CANDIDATES:
    if responds(port):
        print(f"RUNNING:{port}")
        sys.exit(0)

    if not can_bind(port):
        clear_port(port)

    if can_bind(port):
        print(port)
        sys.exit(0)

print("No free port in 9000–9040", file=sys.stderr)
sys.exit(1)
PY
)"

if [[ "$PORT" == RUNNING:* ]]; then
  P="${PORT#RUNNING:}"
  echo "[ok] Dashboard already running → http://127.0.0.1:$P"
  exit 0
fi

python3 -m pip install -q -r requirements.txt 2>/dev/null || true
URL="http://127.0.0.1:$PORT"
echo "$URL" > "$DIR/DASHBOARD_URL.txt"
echo "[ok] Dashboard → $URL"
if [[ "$PORT" != "9000" ]]; then
  echo "[note] Port 9000 does NOT work on this Mac — use $URL"
fi
if command -v open >/dev/null 2>&1; then
  open "$URL" 2>/dev/null || true
fi
exec python3 -m uvicorn app:app --host 127.0.0.1 --port "$PORT"
