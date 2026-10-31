#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/frontend"
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

echo "Starting MORS Vue 3 Frontend on http://localhost:5173..."
exec npm run dev
