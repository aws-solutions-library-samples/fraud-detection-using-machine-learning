##############################################################################
#  Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.   #
#                                                                            #
#  Licensed under the Amazon Software License (the "License"). You may not   #
#  use this file except in compliance with the License. A copy of the        #
#  License is located at                                                     #
#                                                                            #
#      http://aws.amazon.com/asl/                                            #
#                                                                            #
#  or in the "license" file accompanying this file. This file is distributed #
#  on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,        #
#  express or implied. See the License for the specific language governing   #
#  permissions and limitations under the License.                            #
##############################################################################
import json
import os
import boto3
import random
import datetime
import re

def lambda_handler(event, context):
    data_payload = get_data(event, context)
    if not data_payload:
        return
    pred = get_fraud_prediction(data_payload)
    transformed_data = postprocess_event(event, pred)
    response = store_data_prediction(transformed_data)
    print(response)

def get_data(event, context):
    if random.random() < 0.15:
        return
    non_fraud_example = [1.00000000e+00, -9.66271698e-01, -1.85226008e-01, 1.79299331e+00, -8.63291264e-01, -1.03088794e-02, 1.24720311e+00, 2.37608939e-01,
                         3.77435863e-01, -1.38702404e+00, -5.49519211e-02, -2.26487264e-01, 1.78228229e-01, 5.07756889e-01, -2.87923753e-01, -6.31418109e-01,
                         -1.05964720e+00, -6.84092760e-01, 1.96577501e+00, -1.23262203e+00, -2.08037779e-01, -1.08300455e-01, 5.27359685e-03, -1.90320522e-01,
                         -1.17557538e+00, 6.47376060e-01, -2.21928850e-01, 6.27228469e-02, 6.14576302e-02, 1.23500000e+02]
    fraud_example = [4.0600000e+02, -2.3122265e+00, 1.9519920e+00, -1.6098508e+00, 3.9979055e+00, -5.2218789e-01, -1.4265453e+00, -2.5373874e+00,
                     1.3916572e+00, -2.7700894e+00, -2.7722721e+00, 3.2020333e+00, -2.8999074e+00, -5.9522188e-01, -4.2892537e+00, 3.8972411e-01, -1.1407472e+00,
                     -2.8300557e+00, -1.6822468e-02, 4.1695571e-01, 1.2691055e-01, 5.1723236e-01, -3.5049368e-02, -4.6521106e-01, 3.2019821e-01, 4.4519167e-02,
                     1.7783980e-01, 2.6114500e-01, -1.4327587e-01, 0.0000000e+00]
    examples = [fraud_example, non_fraud_example]
    idx = 1
    if random.random() < 0.05:
        idx = 0
    return ','.join(map(str, examples[idx]))

def get_fraud_prediction(data):
    sagemaker_endpoint_name = 'fraud-detection-endpoint'
    sagemaker_runtime = boto3.client('sagemaker-runtime')
    response = sagemaker_runtime.invoke_endpoint(EndpointName=sagemaker_endpoint_name, ContentType='text/csv',
                                                 Body=data)
    print(response)
    result = json.loads(response['Body'].read().decode())
    print(result)
    pred = int(result['predictions'][0]['predicted_label'])
    return pred

def postprocess_event(event, pred):
    millisecond_regex = r'\.\d+'
    timestamp = re.sub(millisecond_regex, '', str(datetime.datetime.now()))
    source = random.choice(['Mobile', 'Web', 'Store'])
    return [timestamp, 'random_id', source, str(pred)]

def store_data_prediction(data):
    firehose_delivery_stream = 'fraud-detection-firehose-stream'
    firehose = boto3.client('firehose', region_name=os.environ['AWS_REGION'])
    record = ','.join(data) + '\n'
    response = firehose.put_record(DeliveryStreamName=firehose_delivery_stream, Record={'Data': record})
    return response
