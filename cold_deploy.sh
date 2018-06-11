#!/usr/bin/env bash

# In this file, we will handle all necessary steps for launching the application:
# 1. install all requirements
# 2. initialize database connection, create models
# 3. load baseline model, as well as data pre-processing lookup tables
# 4. Launch Flask application

# create environment
conda create --name emp_churn python=3.6 -y

# source activate environment
source activate emp_churn

# load requirements
pip install -r requirements.txt

# initialize baseline model
python HRmodel.py

# instantiate database context
python sqlite_declarative.py

# launch server
gunicorn --bind 0.0.0.0:8080 wsgi:app
