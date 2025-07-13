#!/usr/bin/env bash
set -o errexit

echo "✅ Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "📦 Collecting static files..."
python manage.py collectstatic --no-input

echo "🧱 Running migrations..."
python manage.py makemigrations --no-input
python manage.py migrate --no-input

echo "✅ Build completed."