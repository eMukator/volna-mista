#!/bin/bash
set -e

uvicorn api.main:app --host 127.0.0.1 --port 8000 &
uvicorn_pid=$!

nginx -g "daemon off;" &
nginx_pid=$!

# ponytail: single container runs both processes to fit Miget free tier's
# per-app RAM floor; if either dies, exit so `restart: unless-stopped` recovers both.
wait -n "$uvicorn_pid" "$nginx_pid"
exit_code=$?
kill "$uvicorn_pid" "$nginx_pid" 2>/dev/null || true
exit "$exit_code"
