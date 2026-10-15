#!/usr/bin/env bash
# Container entrypoint: FastAPI on 127.0.0.1:8000 (internal), Next.js on $PORT (public).
# Next.js proxies /api/* to FastAPI. If either process exits, the container exits so Cloud Run restarts it.
set -euo pipefail

uvicorn app.main:app --app-dir /app/backend --host 127.0.0.1 --port 8000 &

for _ in $(seq 1 60); do
  python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=1)" 2>/dev/null && break
  sleep 0.5
done

PORT="${PORT:-8080}" HOSTNAME=0.0.0.0 node /app/frontend/server.js &

trap 'kill 0' TERM INT
wait -n
exit $?
