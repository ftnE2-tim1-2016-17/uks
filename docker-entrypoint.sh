#!/bin/bash
echo ******************Prepare database migrations*****************************
python3 ticket_system/manage.py makemigrations #create database migrations
echo **************************************************************************
echo
echo ******************Apply database migrations*******************************
python3 ticket_system/manage.py migrate                # apply database migrations
echo **************************************************************************
echo
echo ******************RUN LOCAL SERVER****************************************
python ticket_system/manage.py runserver 0.0.0.0:8000 --settings=ticket_system.settings_docker # run local server 
echo **************************************************************************
