import os
import sys

# Access environment variables from the .env file and airflow.
ROADR_API_TOKEN_X_AUTH_TOKEN = os.environ.get("ROADR_API_TOKEN_X_AUTH_TOKEN")
ROADR_API = os.environ.get("ROADR_API")
AIRFLOW_PROJ_DIR = os.environ.get("AIRFLOW_HOME")

sys.path.append(AIRFLOW_PROJ_DIR)
from dags.development.mongodb_api import _check_mongodb_api_connection  # noqa: E402


def test_check_mongodb_api_connection():
    # Test case 1: successful connection
    api_token = ROADR_API_TOKEN_X_AUTH_TOKEN
    url = ROADR_API
    assert _check_mongodb_api_connection(api_token, url)

    # # Test case 2: unsuccessful connection (timeout)
    # api_token = "xyz789"
    # url = ROADR_API
    # assert not _check_mongodb_api_connection(api_token, url)
