#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/backend"
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt
fi

echo "Starting MORS FastAPI Backend on http://127.0.0.1:8000..."
exec .venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --reload
