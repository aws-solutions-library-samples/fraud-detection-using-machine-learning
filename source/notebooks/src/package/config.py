from dotenv import load_dotenv
import os
from pathlib import Path

from package import utils

current_folder = utils.get_current_folder(globals())
env_location = '../../../../.env'
dotenv_filepath = Path(current_folder, env_location).resolve()
assert dotenv_filepath.exists(), "Could not find .env file at {}".format(str(dotenv_filepath))

load_dotenv()

STACK_NAME = os.environ['FRAUD_STACK_NAME']
AWS_ACCOUNT_ID = os.environ['AWS_ACCOUNT_ID']
AWS_REGION = os.environ['AWS_REGION']
SAGEMAKER_IAM_ROLE = os.environ['SAGEMAKER_IAM_ROLE']
SOLUTIONS_S3_BUCKET = os.environ['SOLUTIONS_S3_BUCKET']

MODEL_DATA_S3_BUCKET = os.environ['MODEL_DATA_S3_BUCKET']
REST_API_GATEWAY = os.environ['REST_API_GATEWAY']
