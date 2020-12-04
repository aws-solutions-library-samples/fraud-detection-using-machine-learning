import json
from pathlib import Path

from package import utils

current_folder = utils.get_current_folder(globals())
cfn_stack_outputs_filepath = Path(current_folder, '../../../stack_outputs.json').resolve()
assert cfn_stack_outputs_filepath.exists(), "Could not find stack_outputs.json file at {}".format(
    str(cfn_stack_outputs_filepath))

with open(cfn_stack_outputs_filepath) as f:
    cfn_stack_outputs = json.load(f)

STACK_NAME = cfn_stack_outputs['FraudStackName']
SOLUTION_PREFIX = cfn_stack_outputs['SolutionPrefix']
AWS_ACCOUNT_ID = cfn_stack_outputs['AwsAccountId']
AWS_REGION = cfn_stack_outputs['AwsRegion']
SAGEMAKER_IAM_ROLE = cfn_stack_outputs['IamRole']
MODEL_DATA_S3_BUCKET = cfn_stack_outputs['ModelDataBucket']
SOLUTIONS_S3_BUCKET = cfn_stack_outputs['SolutionsS3Bucket']
REST_API_GATEWAY = cfn_stack_outputs['RESTAPIGateway']
SOLUTION_NAME = cfn_stack_outputs['SolutionName']
TEST_OUTPUTS_S3_BUCKET = cfn_stack_outputs.get('TestOutputsS3Bucket', "")
SAGEMAKER_MODE = cfn_stack_outputs['SagemakerMode']
