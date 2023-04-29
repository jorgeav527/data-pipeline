import os
import sys

# Access environment variables from the .env file and airflow.
AIRFLOW_PROJ_DIR = os.environ.get("AIRFLOW_HOME")

sys.path.append(AIRFLOW_PROJ_DIR)
from dags.helpers.boto3_client import client_connection  # noqa: E402


def test_client_connection():
    # Call the function to get an S3 client object
    s3_client = client_connection()

    # Assert that the returned object is not None and has a valid attribute (e.g. `list_buckets`)
    assert s3_client is not None
    assert hasattr(s3_client, "list_buckets")
