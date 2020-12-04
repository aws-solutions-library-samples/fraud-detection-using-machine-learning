import boto3
import sys
import time

sys.path.append('./site-packages')
from crhelper import CfnResource

helper = CfnResource()


@helper.create
def on_create(_, __):
    pass

@helper.update
def on_update(_, __):
    pass


def delete_sagemaker_endpoint(endpoint_name):
    sagemaker_client = boto3.client("sagemaker")
    try:
        sagemaker_client.delete_endpoint(EndpointName=endpoint_name)
        print(
            "Successfully deleted endpoint "
            "called '{}'.".format(endpoint_name)
        )
    except sagemaker_client.exceptions.ClientError as e:
        if "Could not find endpoint" in str(e):
            print(
                "Could not find endpoint called '{}'. "
                "Skipping delete.".format(endpoint_name)
            )
        else:
            raise e


def delete_sagemaker_endpoint_config(endpoint_config_name):
    sagemaker_client = boto3.client("sagemaker")
    try:
        sagemaker_client.delete_endpoint_config(
            EndpointConfigName=endpoint_config_name
        )
        print(
            "Successfully deleted endpoint configuration "
            "called '{}'.".format(endpoint_config_name)
        )
    except sagemaker_client.exceptions.ClientError as e:
        if "Could not find endpoint configuration" in str(e):
            print(
                "Could not find endpoint configuration called '{}'. "
                "Skipping delete.".format(endpoint_config_name)
            )
        else:
            raise e


def delete_sagemaker_model(model_name):
    sagemaker_client = boto3.client("sagemaker")
    try:
        sagemaker_client.delete_model(ModelName=model_name)
        print("Successfully deleted model called '{}'.".format(model_name))
    except sagemaker_client.exceptions.ClientError as e:
        if "Could not find model" in str(e):
            print(
                "Could not find model called '{}'. "
                "Skipping delete.".format(model_name)
            )
        else:
            raise e


def delete_s3_objects(bucket_name):
    s3_resource = boto3.resource("s3")
    try:
        s3_resource.Bucket(bucket_name).objects.all().delete()
        print(
            "Successfully deleted objects in bucket "
            "called '{}'.".format(bucket_name)
        )
    except s3_resource.meta.client.exceptions.NoSuchBucket:
        print(
            "Could not find bucket called '{}'. "
            "Skipping delete.".format(bucket_name)
        )


def delete_s3_bucket(bucket_name):
    s3_resource = boto3.resource("s3")
    try:
        s3_resource.Bucket(bucket_name).delete()
        print(
            "Successfully deleted bucket "
            "called '{}'.".format(bucket_name)
        )
    except s3_resource.meta.client.exceptions.NoSuchBucket:
        print(
            "Could not find bucket called '{}'. "
            "Skipping delete.".format(bucket_name)
        )


def bucket_delete_retry(bucket_name):
    # Try to empty the bucket then delete the model-data bucket 5 times
    # This is needed because the thread we open
    s3_client = boto3.client("s3")
    for _ in range(5):
        delete_s3_objects(bucket_name)
        delete_s3_bucket(bucket_name)

        # Give the delete op time to finish
        time.sleep(10)

        try:
            _ = s3_client.head_bucket(Bucket=bucket_name)
        except s3_client.exceptions.ClientError:
            break  # This is good, the bucket was deleted, so we just exit the loop

        # Otherwise wait a minute and try again
        time.sleep(60)


@helper.delete
def on_delete(event, __):
    # remove sagemaker endpoints
    solution_prefix = event["ResourceProperties"]["SolutionPrefix"]
    endpoint_names = [
        "{}-rcf".format(solution_prefix),
        "{}-xgb".format(solution_prefix),
        "{}-xgb-smote".format(solution_prefix)
    ]
    for endpoint_name in endpoint_names:
        delete_sagemaker_model(endpoint_name)
        delete_sagemaker_endpoint_config(endpoint_name)
        delete_sagemaker_endpoint(endpoint_name)

    # delete buckets
    model_data_bucket = event["ResourceProperties"]["ModelDataBucketName"]
    output_bucket = event["ResourceProperties"]["OutputBucketName"]
    bucket_delete_retry(model_data_bucket)
    bucket_delete_retry(output_bucket)


def handler(event, context):
    helper(event, context)
