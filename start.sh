#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

if [ "$FLASK_DEBUG" = "False" ]
then
    echo "Creating the database tables..."
    python runserver.py flask db init
    python runserver.py flask init_db
    echo "Tables created"
fi

exec "$@"
