#!/usr/bin/env bash
set -euo pipefail

export PORT="${PORT:-8080}"

# Auto public URL for Open buttons (Railway sets RAILWAY_PUBLIC_DOMAIN)
if [[ -z "${PUBLIC_BASE_URL:-}" && -n "${RAILWAY_PUBLIC_DOMAIN:-}" ]]; then
  export PUBLIC_BASE_URL="https://${RAILWAY_PUBLIC_DOMAIN}"
fi

mkdir -p /app/outputs/b1-artifact-inventory \
         /app/outputs/b2-endpoint-map \
         /app/outputs/b3-test-results \
         /app/outputs/uploads

envsubst '${PORT}' < /app/docker/nginx.conf.template > /etc/nginx/conf.d/default.conf
rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true

cat > /usr/local/bin/eval-healthcheck <<EOF
#!/bin/sh
curl -sf "http://127.0.0.1:${PORT}/api/ping" || exit 1
EOF
chmod +x /usr/local/bin/eval-healthcheck

echo "[docker] Command Center on port ${PORT}"
echo "[docker] PUBLIC_BASE_URL=${PUBLIC_BASE_URL:-<local>}"

exec supervisord -n -c /app/docker/supervisord.conf
