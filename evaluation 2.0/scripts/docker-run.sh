#!/usr/bin/env bash
# Build and run all 4 Evaluation 2.0 services in one container.
set -euo pipefail
DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$DIR"

if ! docker info >/dev/null 2>&1; then
  echo "[error] Docker is not running."
  echo "        Start Docker Desktop or OrbStack, then run this script again."
  exit 1
fi

CMD="${1:-up}"
case "$CMD" in
  up)
    docker compose up --build -d
    echo ""
    echo "[ok] All services running in Docker"
    echo "     Dashboard:        http://127.0.0.1:8080"
    echo "     Transactions:     http://127.0.0.1:8080/services/tx/docs"
    echo "     Fraud score API:  http://127.0.0.1:8080/services/fraud/docs"
    echo "     Fintech demo:     http://127.0.0.1:8080/services/fintech/docs"
    echo ""
    echo "Logs:  bash scripts/docker-run.sh logs"
    echo "Stop:  bash scripts/docker-run.sh down"
    ;;
  down)
    docker compose down
    ;;
  logs)
    docker compose logs -f
    ;;
  build)
    docker compose build
    ;;
  *)
    echo "Usage: $0 [up|down|logs|build]"
    exit 1
    ;;
esac
