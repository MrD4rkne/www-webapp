#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Launch app
gunicorn www-project.wsgi