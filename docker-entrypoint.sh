#!/bin/bash
echo ******************Prepare database migrations*****************************
python3 ticket_system/manage.py makemigrations --settings=ticket_system.settings_docker        #create database migrations
echo **************************************************************************
echo .
echo ******************Apply database migrations*******************************
python3 ticket_system/manage.py migrate --settings=ticket_system.settings_docker               # apply database migrations
echo **************************************************************************
echo .
echo ******************Insert initial data*************************************
python3 ticket_system/manage.py loaddata ticket_system/app/fixtures/InitialData.yaml --settings=ticket_system.settings_docker # insert initial data
echo **************************************************************************
echo .
echo ******************RUN LOCAL SERVER****************************************
python ticket_system/manage.py runserver 0.0.0.0:8000 --settings=ticket_system.settings_docker # run local server 
echo **************************************************************************
