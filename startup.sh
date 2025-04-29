#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Collect static
python manage.py collectstatic --noinput

# Launch app
gunicorn www-project.wsgi