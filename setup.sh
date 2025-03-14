#!/bin/bash

echo - SETUP ENVIRONMENT....
python -m venv .env
source .env/Scripts/activate

echo - INSTALL PACKAGES....
pip install -r requirements.txt

echo - START PROJECT....
python manage.py runserver

