#!/bin/bash
echo Prepare database migrations           # Create database migrations
python3 manage.py makemigrations app
echo Apply database migrations
python3 manage.py migrate app              # Apply database migrations

#echo Collect static files
#python3 manage.py collectstatic --noinput  # Collect static files

#run server
#echo starting DEV server
#python3 manage.py runserver

# Prepare log files and start outputting logs to stdout
#touch /srv/logs/gunicorn.log
#touch /srv/logs/access.log
#tail -n 0 -f /srv/logs/*.log &

# Start Gunicorn processes
echo Starting Gunicorn.
exec gunicorn wsgi:application \
    --name uks-project \
    --bind 0.0.0.0:8000 \
    --workers 1 \
    "$@"
#    --log-level=info \
#    --log-file=/srv/logs/gunicorn.log \
#    --access-logfile=/srv/logs/access.log \
#    "$@"

