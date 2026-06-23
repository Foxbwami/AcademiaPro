#!/usr/bin/env bash
set -e

# Force redeploy
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Starting gunicorn..."
exec python -m gunicorn --bind 0.0.0.0:${PORT:-8000} run:app

