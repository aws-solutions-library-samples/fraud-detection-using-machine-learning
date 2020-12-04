import os
import time
import logging

import boto3
import papermill as pm
import watchtower

from package import config, utils


if __name__ == "__main__":

    run_on_start = False if config.TEST_OUTPUTS_S3_BUCKET == "" else True

    if not run_on_start:
        exit()

    cfn_client = boto3.client('cloudformation', region_name=config.AWS_REGION)

    # Set up logging through watchtower
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    log_group = "/aws/sagemaker/NotebookInstances"
    stream_name = "{}/run-notebook.log".format(utils.get_notebook_name())
    logger.addHandler(
        watchtower.CloudWatchLogHandler(log_group=log_group, stream_name=stream_name))
    # Add papermill logging to CloudWatch as well
    pm_logger = logging.getLogger('papermill')
    pm_logger.addHandler(
        watchtower.CloudWatchLogHandler(log_group=log_group, stream_name=stream_name))

    # Wait for the stack to finish launching
    logger.info("Waiting for stack to finish launching...")
    waiter = cfn_client.get_waiter('stack_create_complete')

    waiter.wait(StackName=config.STACK_NAME)

    logger.info("Starting notebook execution through papermill")

    # Run the notebook
    bucket = config.TEST_OUTPUTS_S3_BUCKET
    prefix = 'integration-test'
    output_notebook = "output.ipynb"

    start_time = time.time()
    test_prefix = "/home/ec2-user/SageMaker/test/"
    with open(os.path.join(test_prefix, "output_stdout.txt"), 'w') as stdoutfile, open(os.path.join(test_prefix, "output_stderr.txt"), 'w') as stderrfile:
        try:
            nb = pm.execute_notebook(
                '/home/ec2-user/SageMaker/notebooks/sagemaker_fraud_detection.ipynb',
                os.path.join(test_prefix, output_notebook),
                cwd='/home/ec2-user/SageMaker/notebooks/',
                kernel_name='python3',
                stdout_file=stdoutfile, stderr_file=stderrfile, log_output=True
            )
        except pm.PapermillExecutionError as err:
            logger.warn("Notebook encountered execution error: {}".format(err))
        finally:
            end_time = time.time()
            logger.info("Notebook execution time: {} sec.".format(end_time - start_time))
            s3 = boto3.resource('s3')
            # Upload notebook output file to S3
            s3.meta.client.upload_file(
                os.path.join(test_prefix, output_notebook), bucket, os.path.join(prefix, output_notebook))
            s3.meta.client.upload_file(
                os.path.join(test_prefix, "output_stdout.txt"), bucket, os.path.join(prefix, "output_stdout.txt"))
            s3.meta.client.upload_file(
                os.path.join(test_prefix, "output_stderr.txt"), bucket, os.path.join(prefix, "output_stderr.txt"))
