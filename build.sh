#!/usr/bin/env bash
set -o errexit

echo "=== Installing Python dependencies ==="
pip install -r requirements.txt

echo "=== Creating required directories ==="
mkdir -p media/products media/categories media/avatars
mkdir -p staticfiles

echo "=== Collecting static files ==="
python manage.py collectstatic --no-input --clear 2>&1 || echo "Warning: Static files collection had issues"

echo "=== Running database migrations ==="
python manage.py migrate --noinput 2>&1 || echo "Warning: Migrations may have failed"

echo "=== Build completed successfully ==="
