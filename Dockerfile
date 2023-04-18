FROM apache/airflow:2.5.1-python3.8

COPY requirements.txt pyproject.toml /opt/airflow/
RUN pip install --no-cache-dir -r /opt/airflow/requirements.txt
