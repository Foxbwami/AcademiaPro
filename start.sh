#!/bin/bash
set -e

echo "Starting gunicorn..."
exec python -m gunicorn --bind 0.0.0.0:${PORT:-8000} run:app
