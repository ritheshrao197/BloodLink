#!/usr/bin/env bash
# Production entry point: runs the API (which also serves the built web app) and the Telegram bot in one service.
set -e
PORT="${PORT:-8000}"
export BLOODLINK_API_URL="${BLOODLINK_API_URL:-http://127.0.0.1:$PORT/api}"
ROOT="$(cd "$(dirname "$0")" && pwd)"

if [ -n "$TELEGRAM_BOT_TOKEN" ]; then
  ( cd "$ROOT/bot" && until python bot.py; do echo "bot exited, restarting in 5s"; sleep 5; done ) &
fi
cd "$ROOT/backend"
exec python -m uvicorn main:app --host 0.0.0.0 --port "$PORT"
