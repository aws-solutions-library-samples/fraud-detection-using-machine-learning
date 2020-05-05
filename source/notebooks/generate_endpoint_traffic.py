import time
import boto3
import json
import re
import datetime
import random

import requests
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth
import numpy as np
from scipy.stats import poisson

lambda_client = boto3.client('lambda')
lambda_function = 'fraud-detection-event-processor'
region = boto3.Session().region_name

def generate_metadata():
    millisecond_regex = r'\.\d+'
    timestamp = re.sub(millisecond_regex, '', str(datetime.datetime.now()))
    source = random.choice(['Mobile', 'Web', 'Store'])
    result = [timestamp, 'random_id', source]

    return result

def get_data_payload(test_array):
    return {'data':','.join(map(str, test_array)),
            'metadata': generate_metadata()}

def generate_traffic(X_test):
    while True:
        np.random.shuffle(X_test)
        for example in X_test:
            data_payload = get_data_payload(example)
            invoke_endpoint(data_payload)
            # We invoke the function according to a shifted Poisson distribution
            # to simulate data arriving at random intervals
            time.sleep(poisson.rvs(1, size=1)[0] + np.random.rand())

def invoke_endpoint(payload):
    # We get credentials from the IAM role of the notebook instance, then use them to create a signed request to the API Gateway
    auth = BotoAWSRequestsAuth(aws_host="fraud-detection-api-placeholder.execute-api.{}.amazonaws.com".format(region),
                           aws_region=region,
                           aws_service='execute-api')

    invoke_url = "https://fraud-detection-api-placeholder.execute-api.{}.amazonaws.com/prod/invocations".format(region)

    # We don't use the response here, as the Lambda function will log any calls to it.
    response = requests.post(invoke_url, json=payload, auth=auth)
