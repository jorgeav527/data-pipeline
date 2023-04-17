import os
from datetime import datetime, timedelta

from airflow.models import DAG
from airflow.operators.email import EmailOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.http.sensors.http import HttpSensor
from development.mongodb_api import _fetch_mongo_api_to_json, _transform_users_to_csv
from development.rdstationcmr_api import _fetch_rdstudioapicmr_contacts_to_json, _transform_contacts_to_csv
from helpers.boto3_client import client_connection
from helpers.dev_helpers import _create_sql_file, _inject_sql_file_to_postgres
from helpers.variables_mongodb_api import _create_users_sql_table, _users_colum_names
from helpers.variables_rdstation_api import _contacts_colum_names, _create_contacts_sql_table

RDSTATION_API_TOKEN = os.environ.get("RDSTATION_API_TOKEN")
ROADR_API_TOKEN_X_AUTH_TOKEN = os.environ.get("ROADR_API_TOKEN_X_AUTH_TOKEN")

default_args = {
    "owner": "jorgeav527",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "email": "jv@roadr.com",
    "email_on_success": False,
    "email_on_failure": False,
    "ds": "{{ ds }}",
}

with DAG(
    default_args=default_args,
    dag_id="ETL_develoment_v11",
    start_date=datetime(2023, 4, 1),
    schedule="@daily",  # will be "@daily"
    catchup=True,
    tags=["rd_studio_api"],
    template_searchpath="bucket",
) as dag:
    ####################################################
    # CONTACTS (RD Station CMR API (contacts))
    ####################################################

    # Define the HttpSensor to check if the connection is OK
    check_api_rdstationcmr_connection = HttpSensor(
        task_id="check_api_rdstationcmr_connection",
        http_conn_id="RD_Studio_API",  # https://crm.rdstation.com/api/v1/contacts?token=MyToken&page=Page&limit=Limit&q=Query # noqa: E501
        endpoint=f"contacts?token={RDSTATION_API_TOKEN}",
        response_check=lambda response: response.status_code == 200,
        poke_interval=60,  # check the API connection every 60 seconds
        timeout=120,  # wait up to 120 seconds for a successful connection
    )

    # Define the PythonOperator to fetch and save contacts
    fetch_rdstudioapicmr_contacts_to_json = PythonOperator(
        task_id="fetch_rdstudioapicmr_contacts_to_json",
        python_callable=_fetch_rdstudioapicmr_contacts_to_json,
        op_kwargs={
            "extracted_path": "bucket/extracted_data/rdstationcmr_contacts_{{ds}}.json",
            # "contacts_url": "https://crm.rdstation.com/api/v1/contacts?token={RDSTATION_API_TOKEN}",
        },
    )

    # Define the PythonOperator to transform and save contacts
    transform_contacts_to_csv = PythonOperator(
        task_id="transform_contacts_to_csv",
        python_callable=_transform_contacts_to_csv,
        op_kwargs={
            "extracted_path": "bucket/extracted_data/rdstationcmr_contacts_{{ds}}.json",
            "transformed_path": "bucket/transformed_data/rdstationcmr_contacts_{{ds}}.csv",
        },
    )

    create_contacts_sql_table = SQLExecuteQueryOperator(
        task_id="create_contacts_sql_table",
        sql=_create_contacts_sql_table,
        conn_id="Postgres_ID",
    )

    # Create a PythonOperator to create a sql file
    create_sql_contacts = PythonOperator(
        task_id="create_sql_contacts",
        python_callable=_create_sql_file,
        op_kwargs={
            "columns": _contacts_colum_names,
            "transformed_path": "bucket/transformed_data/rdstationcmr_contacts_{{ds}}.csv",
            "loaded_path": "bucket/loaded_data/rdstationcmr_contacts_{{ds}}.sql",
            "table_name": "contacts",
        },
    )

    # Inject the sql file into PostgresDB
    insert_contacts_to_postgres = PythonOperator(
        task_id="insert_contacts_to_postgres",
        python_callable=_inject_sql_file_to_postgres,
        op_kwargs={
            "loaded_path": "bucket/loaded_data/rdstationcmr_contacts_{{ds}}.sql",
        },
    )

    ##################################
    # USERS (mongoDB(users))
    ##################################

    # Set up the MongoDb API Sensor operator
    check_mongodb_api_connection = HttpSensor(
        task_id="check_mongodb_api_connection",
        http_conn_id="Mongo_DB_API",
        endpoint="api/user/allusers",
        headers={"x-auth-token": ROADR_API_TOKEN_X_AUTH_TOKEN},
        response_check=lambda response: response.status_code == 200,
        poke_interval=60,  # check the API connection every 60 seconds
        timeout=120,  # wait up to 120 seconds for a successful connection
    )

    # Define the PythonOperator to fetch and save users
    fetch_mongo_api_to_json = PythonOperator(
        task_id="fetch_mongo_api_to_json",
        python_callable=_fetch_mongo_api_to_json,
        op_kwargs={
            "users_url": "http://192.168.0.13:3000/api/user/allusers?start_day=2022-07-27&end_day=2022-07-28",
            # "users_url": "http://192.168.0.13:3000/api/user/allusers?start_day={{data_interval_start.year}}-{{data_interval_start.month}}-{{data_interval_start.day}}&end_day={{data_interval_end.year}}-{{data_interval_end.month}}-{{data_interval_end.day}}", # noqa: E501
            "extracted_path": "bucket/extracted_data/mongodb_api_users_{{ds}}.json",
            "bucket_key_path": "extracted_data/mongodb_api/users/{{ds}}.json",
            "client": client_connection(),
        },
    )

    # Define the PythonOperator to transform and save users
    transform_users_to_csv = PythonOperator(
        task_id="transform_users_to_csv",
        python_callable=_transform_users_to_csv,
        op_kwargs={
            "extracted_url": "https://roadr-data-lake.us-southeast-1.linodeobjects.com/extracted_data/mongodb_api/users/{{ds}}.json",  # noqa: E501
            "transformed_path": "bucket/transformed_data/mongodb_api_users_{{ds}}.csv",
            "bucket_key_path": "transformed_data/mongodb_api/users/{{ds}}.csv",
            "client": client_connection(),
        },
    )

    create_users_sql_table = SQLExecuteQueryOperator(
        task_id="create_users_sql_table",
        sql=_create_users_sql_table,
        conn_id="Postgres_ID",
    )

    # Create a PythonOperator to create a sql file
    create_sql_users = PythonOperator(
        task_id="create_sql_users",
        python_callable=_create_sql_file,
        op_kwargs={
            "columns": _users_colum_names,
            "transformed_url": "https://roadr-data-lake.us-southeast-1.linodeobjects.com/transformed_data/mongodb_api/users/{{ds}}.csv",  # noqa: E501
            "loaded_path": "bucket/loaded_data/mongodb_api_users_{{ds}}.sql",
            "bucket_key_path": "loaded_data/mongodb_api/users/{{ds}}.sql",
            "table_name": "users",
            "client": client_connection(),
        },
    )

    # Inject the sql file into PostgresDB
    insert_users_to_postgres = PythonOperator(
        task_id="insert_users_to_postgres",
        python_callable=_inject_sql_file_to_postgres,
        op_kwargs={
            "loaded_url": "https://roadr-data-lake.us-southeast-1.linodeobjects.com/loaded_data/mongodb_api/users/{{ds}}.sql",  # noqa: E501
        },
    )

    ##################################
    # Others
    ##################################

    # Empty operator
    start = EmptyOperator(task_id="start")
    end = EmptyOperator(task_id="end")

    # Send report as a email status
    send_email_report_status = EmailOperator(
        task_id="send_email_report_status",
        to="jv@roadr.com",
        subject="Airflow Report - {{ ds }}",
        html_content="""<h3>Task Report for {{ ds }}</h3>
                    <p>Successful tasks:</p>
                    <ul>
                        {% for task in dag.tasks %}
                            {% if task.task_id != 'send_email' and task.task_id.endswith('_success') %}
                                <li>{{ task.task_id }} - {{ task.execution_date }}</li>
                            {% endif %}
                        {% endfor %}
                    </ul>""",
    )

    start >> [check_api_rdstationcmr_connection, check_mongodb_api_connection]
    (
        check_api_rdstationcmr_connection
        >> fetch_rdstudioapicmr_contacts_to_json
        >> transform_contacts_to_csv
        >> create_contacts_sql_table
        >> create_sql_contacts
        >> insert_contacts_to_postgres
    )
    (
        check_mongodb_api_connection
        >> fetch_mongo_api_to_json
        >> transform_users_to_csv
        >> create_users_sql_table
        >> create_sql_users
        >> insert_users_to_postgres
    )
    (
        [
            insert_contacts_to_postgres,
            insert_users_to_postgres,
        ]
        >> send_email_report_status
        >> end
    )
