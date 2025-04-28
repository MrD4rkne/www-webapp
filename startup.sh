#!/bin/bash

# Zainstaluj zależności
pip install -r requirements.txt

# Uruchom aplikację
gunicorn www-project.wsgi