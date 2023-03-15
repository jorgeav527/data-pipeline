import json
from datetime import datetime, timedelta
import os

from airflow.models import DAG
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import SimpleHttpOperator

from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

default_arg = {
    "owner": "jorgeav527",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}
cwd = os.getcwd()

TOKEN = "63fec468e1dca1000c53a7e5"


def save_contacts(ti) -> None:
    contacts = ti.xcom_pull(task_ids=["get_contacts"])
    with open("bucket/raw_data/contacts.json", "w") as _file:
        json.dump(contacts[0], _file)


with DAG(
    default_args=default_arg,
    dag_id="ETL_develoment_v4",
    start_date=datetime(2022, 3, 6),
    schedule_interval="@daily",
    catchup=False,
    tags=["rd_studio_api"],
) as dag:
    connection = HttpSensor(
        task_id="connection",
        http_conn_id="RD_Studio_API",
        endpoint=f"users?token={TOKEN}",
    )
    get_users = SimpleHttpOperator(
        task_id="get_users",
        http_conn_id="RD_Studio_API",
        endpoint=f"users?token={TOKEN}",
        method="GET",
        response_filter=lambda response: json.loads(response.text),
        log_response=True,
    )
    get_contacts = SimpleHttpOperator(
        task_id="get_contacts",
        http_conn_id="RD_Studio_API",
        endpoint=f"contacts?token={TOKEN}",
        method="GET",
        response_filter=lambda response: json.loads(response.text),
        log_response=True,
    )
    save_contacts = PythonOperator(
        task_id="save_contacts",
        python_callable=save_contacts,
    )

    connection >> [get_users, get_contacts] >> save_contacts >> connection
