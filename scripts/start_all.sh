#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

"$ROOT_DIR/scripts/start_backend.sh" &
BACKEND_PID=$!

"$ROOT_DIR/scripts/start_frontend.sh" &
FRONTEND_PID=$!

trap 'kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true' INT TERM EXIT
wait
