#!/usr/bin/env bash
set -e

echo "Checking installed packages..."
pip list | grep gunicorn

echo "Starting gunicorn..."
exec python -m gunicorn --bind 0.0.0.0:${PORT:-8000} run:app

