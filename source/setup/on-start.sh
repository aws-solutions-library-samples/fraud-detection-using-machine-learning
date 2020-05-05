#!/bin/bash

# PARAMETERS

ENVIRONMENT=python3

source /home/ec2-user/anaconda3/bin/activate "$ENVIRONMENT"

pip install --upgrade imbalanced-learn
pip install --upgrade aws_requests_auth

source /home/ec2-user/anaconda3/bin/deactivate
