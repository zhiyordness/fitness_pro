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

if [ "$DEBUG" = "True" ]; then
    echo "Starting Django Development Server..."
    exec python manage.py runserver 0.0.0.0:8000
else
    echo "Starting Gunicorn..."
    exec gunicorn fitness_pro.wsgi:application --bind 0.0.0.0:8000
fi

#echo "Starting Gunicorn..."
#
#exec gunicorn fitness_pro.wsgi:application --bind 0.0.0.0:8000

