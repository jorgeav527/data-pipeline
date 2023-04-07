import pytest
import os
import sys

# Add the project directory to the system path
AIRFLOW_PROJ_DIR = os.environ.get("AIRFLOW_HOME")
sys.path.append(AIRFLOW_PROJ_DIR)
from dags.helpers.variables_mongodb_api import _create_users_sql_table

from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.models import DagBag
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from datetime import datetime


@pytest.fixture(scope="session")
def check_mongodb_api_connection():
    # Returns the HttpSensor response for the endpoint of an API session.
    return HttpSensor(
        task_id="check_mongodb_api_connection",
        http_conn_id="Mongo_DB_API",
        endpoint="api/user/allusers",
        headers={
            "x-auth-token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImlkIjoiNjNjODY1ZjM1M2JkZjgyMGY5MjgxNjRjIn0sImlhdCI6MTY3OTM1ODE3N30.krlGV2QiC_KwGcVW38TrlszIPDnb6RSX_ML1Kt206YA"
        },
        poke_interval=60,  # check the API connection every 60 seconds
        timeout=120,  # wait up to 120 seconds for a successful connection
    )


def test_check_mongodb_api_response(check_mongodb_api_connection):
    # Returns the assertion of the succesfull connection to the mongo DB API.
    assert check_mongodb_api_connection.poke(None)


@pytest.fixture(scope="session")
def postgres_hook():
    # Returns a connection with the postgres DB instance session.
    return PostgresHook(postgres_conn_id="Postgres_ID")


def test_create_users_sql_table(postgres_hook):
    # Create a DAG bag to load DAGs from your Airflow project
    dag_bag = DagBag(dag_folder="/dags/dev_dag.py")

    # Get the SQLExecuteQueryOperator task from the DAG
    dag = dag_bag.get_dag(dag_id="ETL_develoment_v11")
    task = dag.get_task(task_id="create_users_sql_table")

    # Call the task's execute method to create the table
    task.execute({})

    # Check if the table exists
    assert (
        postgres_hook.get_records(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')"
        )[0][0]
        is True
    )
