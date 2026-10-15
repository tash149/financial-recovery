#!/usr/bin/env bash
# Run backend (http://localhost:8000) and frontend (http://localhost:3000) together. Ctrl+C stops both.
set -euo pipefail
cd "$(dirname "$0")"

if [ -f .env ]; then set -a; . ./.env; set +a; fi

if [ ! -d backend/.venv ]; then
  python3.11 -m venv backend/.venv
  backend/.venv/bin/pip install -q -r backend/requirements-dev.txt
fi
[ -d frontend/node_modules ] || (cd frontend && npm ci)

trap 'trap - EXIT; kill 0' EXIT INT TERM
(cd backend && .venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000) &
(cd frontend && npm run dev) &
wait
