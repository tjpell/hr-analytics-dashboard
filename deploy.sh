#!/usr/bin/env bash

# source activate environment
source activate emp_churn

# launch server
gunicorn --bind 0.0.0.0:8080 wsgi:app
