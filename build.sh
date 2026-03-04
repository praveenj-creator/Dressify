#!/usr/bin/env bash
set -o errexit

echo "=== Starting Dressify Build ==="
echo ""

echo "=== Step 1: Installing Python dependencies ==="
pip install -r requirements.txt
if [ $? -eq 0 ]; then echo "✓ Dependencies installed successfully"; else echo "✗ Failed to install dependencies"; exit 1; fi
echo ""

echo "=== Step 2: Creating required directories ==="
mkdir -p media/products media/categories media/avatars
mkdir -p staticfiles
echo "✓ Directories created"
echo ""

echo "=== Step 3: Collecting static files ==="
python manage.py collectstatic --noinput --clear
if [ $? -eq 0 ]; then echo "✓ Static files collected"; else echo "⚠ Static files collection had warnings"; fi
echo ""

echo "=== Step 4: Running database migrations ==="
python manage.py migrate --noinput
if [ $? -eq 0 ]; then echo "✓ Migrations completed"; else echo "⚠ Migration warnings (database may not be ready yet)"; fi
echo ""

echo "=== Build completed successfully ==="
echo "Your app is ready to run!"
