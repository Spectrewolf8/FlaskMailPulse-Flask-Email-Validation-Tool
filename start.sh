#!/bin/bash

# Activate your virtual environment, if you have one
# source venv/bin/activate

# Start the Flask application using Gunicorn
gunicorn app:app -w1 --log-file -