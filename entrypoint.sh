#!/bin/sh

set -e

echo "Waiting for PostgreSQL..."

until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"
do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is ready!"

echo "Applying migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Populating food database..."
python manage.py populate_food_database

echo "Populating training database..."
python manage.py populate_training_data

echo "Starting Gunicorn..."

exec gunicorn fitness_pro.wsgi:application --bind 0.0.0.0:8000