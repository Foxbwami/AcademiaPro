#!/usr/bin/env bash
set -e

# Force redeploy
echo "Installing dependencies..."
pip install --break-system-packages -r requirements.txt

echo "Starting gunicorn..."
export PATH="/opt/render/.local/bin:$PATH"
exec gunicorn --bind 0.0.0.0:${PORT:-8000} run:app

