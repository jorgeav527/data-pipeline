import json
from datetime import datetime, timedelta
import pandas as pd
import requests
from glom import glom

from airflow.models import DAG
from airflow.providers.http.sensors.http import HttpSensor
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.email import EmailOperator
from airflow.operators.empty import EmptyOperator


default_args = {
    "owner": "jorgeav527",
    "start_date": datetime(2022, 3, 17),
    "schedule_interval": "@daily",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "email": "jv@roadr.com",
}

TOKEN = "63fec468e1dca1000c53a7e5"
MONGO_URL = "mongodb+srv://roadr_dev:7juzcxuvMpMlyfHO@devcluster.8igvo.mongodb.net/?retryWrites=true&w=majority"


# Connecting with the database.
def _check_mongodb_connection():
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    try:
        # The ping command is cheap and does not require auth.
        print(client.admin.command("ping"))
    except ConnectionFailure as err:
        print(err, "Server not available")


def _fetch_mongodb_users_save():
    # Connecting with the database.
    client = MongoClient(MONGO_URL)
    try:
        # The ping command is cheap and does not require auth.
        print(client.admin.command("ping"))
    except ConnectionFailure as err:
        print(err, "Server not available")

    db_test = client["test"]
    collection = db_test["users"]

    # retrieve documents from collection
    documents = list(collection.find())

    # Users
    # Save the response content to a file
    with open("bucket/extracted_data/mongodb_users.json", "w") as _file:
        json.dump(documents, _file, default=str)


# Define the function to fetch data from the API and save it to a file
def _fetch_rdstudioapicmr_contacts_and_save_data():
    # Make the API request
    response = requests.get(f"https://crm.rdstation.com/api/v1/contacts?token={TOKEN}")
    # Check the response status code
    if response.status_code == 200:
        # Save the response content to a file
        with open("bucket/extracted_data/rdstationcmr_contacts.json", "w") as _file:
            _file.write(response.content.decode())


# Define the function to read the JSON file and transform it into a Pandas DataFrame
def _transform_contacts_save():
    # Read the JSON file into a Pandas DataFrame
    # load data using Python JSON module
    with open("bucket/extracted_data/rdstationcmr_contacts.json", "r") as _file:
        data = json.loads(_file.read())

    expr = (
        "contacts",
        [
            {
                "id": "id",
                "title": "title",
                "facebook": "facebook",
                "linkedin": "linkedin",
                "skype": "skype",
                "created_at": (
                    "created_at",
                    lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%f%z").strftime(
                        "%Y-%m-%d"
                    ),
                ),
                "updated_at": (
                    "updated_at",
                    lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%f%z").strftime(
                        "%Y-%m-%d"
                    ),
                ),
                "email": ("emails", ["email"]),
                "phone": ("phones", ["phone"]),
            }
        ],
    )

    # Use glom to extract the flattened data
    df = pd.DataFrame(glom(data, expr))

    # Save the Pandas DataFrame to a file
    df.to_csv("bucket/transformed_data/rdstationcmr_contacts.csv", index=False)


# Define the function to read the JSON file and transform it into a Pandas DataFrame
def _transform_users_save():
    # Read the JSON file into a Pandas DataFrame
    # load data using Python JSON module
    with open("bucket/extracted_data/mongodb_users.json", "r") as _file:
        data = json.loads(_file.read())

    # Save the Pandas DataFrame to a file
    df = pd.json_normalize(data)
    df.to_csv("bucket/transformed_data/mongodb_users.csv", index=False)


with DAG(
    default_args=default_args,
    dag_id="ETL_develoment_v4",
    start_date=datetime(2022, 3, 16),
    schedule_interval=None,  # will be "@daily"
    catchup=False,
    tags=["rd_studio_api"],
) as dag:
    # Set up the MongoDbSensor operator
    check_mongodb_connection = PythonOperator(
        task_id="check_mongodb_connection",
        python_callable=_check_mongodb_connection,
    )

    # Define the HttpSensor to check if the connection is OK
    check_api_rdstationcmr_connection = HttpSensor(
        task_id="check_api_rdstationcmr_connection",
        http_conn_id="RD_Studio_API",  #  https://crm.rdstation.com/api/v1/contacts?token=MyToken&page=Page&limit=Limit&q=Query
        endpoint=f"contacts?token={TOKEN}",
        response_check=lambda response: response.status_code == 200,
        poke_interval=60,  # check the API connection every 60 seconds
        timeout=120,  # wait up to 120 seconds for a successful connection
    )

    # Define the PythonOperator to execute the function
    fetch_rdstudioapicmr_contacts_and_save_data = PythonOperator(
        task_id="fetch_rdstudioapicmr_contacts_and_save_data",
        python_callable=_fetch_rdstudioapicmr_contacts_and_save_data,
    )

    # Define the PythonOperator to execute the function
    fetch_mongodb_users_save = PythonOperator(
        task_id="fetch_mongodb_users_save",
        python_callable=_fetch_mongodb_users_save,
    )

    # Define the PythonOperator to execute the function
    transform_contacts_save = PythonOperator(
        task_id="transform_contacts_save",
        python_callable=_transform_contacts_save,
    )

    # Define the PythonOperator to execute the function
    transform_users_save = PythonOperator(
        task_id="transform_users_save",
        python_callable=_transform_users_save,
    )
    # Send report as a email status
    send_email_report_status = EmailOperator(
        task_id="send_email_report_status",
        to="jv@roadr.com",
        subject="Airflow Alert",
        html_content=""" <h3>Email Test</h3> """,
    )

    start = EmptyOperator(task_id="start")

    start >> [check_api_rdstationcmr_connection, check_mongodb_connection]
    (
        check_api_rdstationcmr_connection
        >> fetch_rdstudioapicmr_contacts_and_save_data
        >> transform_contacts_save
    )
    (check_mongodb_connection >> fetch_mongodb_users_save >> transform_users_save)
    [
        transform_contacts_save,
        transform_users_save,
    ] >> send_email_report_status
