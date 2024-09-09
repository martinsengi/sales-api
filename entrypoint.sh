#!/bin/bash

# Wait for Postgres
echo "Waiting for PostgreSQL to start..."
while ! nc -z $POSTGRES_HOST 5432; do
  sleep 1
done

python manage.py migrate
python manage.py runserver 0.0.0.0:8000
