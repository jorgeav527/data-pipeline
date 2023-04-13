import boto3
import os

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_ENDPOINT_URL = os.environ.get("AWS_ENDPOINT_URL")


def client_connection():
    linode_obj_config = {
        "aws_access_key_id": AWS_ACCESS_KEY_ID,
        "aws_secret_access_key": AWS_SECRET_ACCESS_KEY,
        "AWS_ENDPOINT_URL": AWS_ENDPOINT_URL,
    }
    client = boto3.client("s3", **linode_obj_config)
    return client
