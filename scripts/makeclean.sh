#!/usr/bin/env bash

# reset the state of the models and all that jazz
rm models/*
rm encodings/*
rm predictions/*

# destroy environment
source deactivate
conda remove --all -n emp_churn -y
