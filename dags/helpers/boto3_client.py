import os

import boto3

# Access environment variables from the .env file.
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_ENDPOINT_URL = os.environ.get("AWS_ENDPOINT_URL")


def client_connection():
    try:
        linode_obj_config = {
            "aws_access_key_id": AWS_ACCESS_KEY_ID,
            "aws_secret_access_key": AWS_SECRET_ACCESS_KEY,
            "endpoint_url": AWS_ENDPOINT_URL,
        }
        client = boto3.client("s3", **linode_obj_config)
        return client

    except Exception as error:
        print("An error occurred while connecting to the S3 client:", error, sep="\n")

    finally:
        # close the S3 client connection in the finally block to ensure proper resource cleanup
        client.close() if client else None
