#!/usr/bin/env bash
set -e

# Ensure user-installed scripts are available during install and runtime.
export PATH="/opt/render/.local/bin:$PATH"

# Force redeploy
echo "Installing dependencies..."
pip install --break-system-packages -r requirements.txt

echo "Starting gunicorn..."
exec gunicorn --bind 0.0.0.0:${PORT:-8000} run:app

