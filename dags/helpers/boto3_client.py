import boto3

AWS_ACCESS_KEY_ID = "3MA6DHBKA62IV4CHEOBB"
AWS_SECRET_ACCESS_KEY = "11vIyS93cAK7HEnejADV9NUnG0rxWMLdiQrxdfyR"
ENDPOINT_URL = "https://us-southeast-1.linodeobjects.com"


def client_connection():
    linode_obj_config = {
        "aws_access_key_id": AWS_ACCESS_KEY_ID,
        "aws_secret_access_key": AWS_SECRET_ACCESS_KEY,
        "endpoint_url": ENDPOINT_URL,
    }
    client = boto3.client("s3", **linode_obj_config)
    return client
