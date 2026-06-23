#!/bin/bash
set -e

echo "Installing/upgrading pip..."
pip install --upgrade pip

echo "Installing requirements..."
pip install -r requirements.txt

echo "Starting gunicorn..."
python -m gunicorn run:app
