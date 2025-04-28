#!/bin/bash

# Zainstaluj zależności
pip install -r requirements.txt

# Zbierz pliki statyczne
python manage.py collectstatic --noinput

# Uruchom aplikację
gunicorn www-project.wsgi