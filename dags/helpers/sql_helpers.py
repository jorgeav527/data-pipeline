import os

import pandas as pd
import psycopg2
import requests

# Access environment variables from the .env file.
DB_USERNAME = os.environ.get("DB_USERNAME")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")


def _create_sql_file(client, transformed_url, loaded_path, bucket_key_path, table_name, columns, **kwargs):
    """
    Sending a GET request to get the transformed daily YYYY-MM-DD.csv file from the bucket file.
    This function should convert the YYYY-MM-DD.csv data file and then convert it to a SQL file format.
    This function also must filter and convert some CSV data into postgrest-compatible SQL queries.

    Args:
    - client (object): Call the boto3 client to connect to the bucket.
    - transformed_url (string): The actual bucket path where the transformed data will be pulled.
    - loaded_path (string): The temporary path (bucket/loaded_data/*.csv) where the data will be saved.
    - bucket_key_path (string): The actual bucket path where the loaded data will be saved.
    - table_name (string): The name of the postgres data table.
    - columns (list): A list of the column names (this information is taken from the CSV file).
    **kwargs:
    - kwargs["ds"] (dictionary): The day that the task ends up happening.

    Returns:
    - A string "SQL file was successfully added to the bucket at ({ds}).". If the data was succesfully transformed.
    """  # noqa: E501

    # Getting the context of the task.
    ds = kwargs["ds"]

    # To debug the parameters.
    print(f"transformed_url: {transformed_url}")
    print(f"loaded_path: {loaded_path}")
    print(f"bucket_key_path: {bucket_key_path}")

    # Read the CSV file into a Pandas dataframe.
    url = transformed_url
    df = pd.read_csv(url)

    # Open the SQL file in write mode.
    with open(loaded_path, "w") as file:
        # Iterate over each row in the dataframe.
        for index, row in df.iterrows():
            # Build the list of values to insert into the SQL statement.
            values = []
            for column in columns:
                # Get the value of the current column for the current row.
                value = row[column]

                # Check the data type of the value and format it appropriately.
                if pd.isna(value):
                    values.append("NULL")
                elif isinstance(value, list):
                    values.append("ARRAY['{}']".format(value))
                elif isinstance(value, int):
                    values.append(str(value))
                elif isinstance(value, pd.Timestamp):
                    values.append("'{}'".format(value.strftime("%Y-%m-%d %H:%M:%S")))
                else:
                    values.append("'{}'".format(str(value).replace("'", '"')))

            # Write the SQL statement to the file.
            file.write("INSERT INTO {} ({}) VALUES ({});\n".format(table_name, ",".join(columns), ",".join(values)))

    # Call the S3 bucket client to save a file.
    client.upload_file(
        Filename=loaded_path,
        Bucket="roadr-data-lake",
        Key=bucket_key_path,
        ExtraArgs={"ACL": "public-read"},
    )

    # Delete the local file.
    os.remove(loaded_path)

    print(f"SQL file was successfully added to the bucket at ({ds}).")


def _inject_sql_to_postgres(sql_table=None, loaded_url=None, **kwargs):
    """
    This function injects sql string text into the Postgres database instance.
    It will be used to inject either two string queries a sql table to be created or to upload a url path to be readed as a sql file and injected into the postgres database.
    Only one parameter could be None.

    Args:
    - loaded_url (string): The actual bucket path where the transformed data will be pulled.
    - sql_table (string): The name of the postgres data table.
    **kwargs:
    - kwargs["ds"] (dictionary): The day that the task ends up happening.

    Returns:
    - A string "Data table has been successfuly created if not created at ({ds}).". If the sql_table is not None. otherwise;
    - A string "The loaded SQL data file has been successfully injected! at {ds}". If the loaded_url is not None.
    """  # noqa: E501

    # Getting the context of the task.
    ds = kwargs["ds"]

    # To debug the parameters.
    print(f"sql_table: {sql_table}")
    print(f"loaded_url: {loaded_url}")

    try:
        # Establish a connection to the PostgreSQL database.
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USERNAME,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )

        # Create a cursor object to execute SQL commands.
        cur = conn.cursor()

        # Create the SQL table if sql_table parameter is not None.
        if sql_table is not None:
            # Execute the SQL script.
            cur.execute(sql_table)

            print(f"Data table has been successfuly created if not created at ({ds}).")

        if loaded_url is not None:
            # Read the SQL file contents.
            response = requests.get(loaded_url)
            sql = response.text

            # Execute the SQL script.
            cur.execute(sql)

            print(f"The loaded SQL data file has been successfully injected! at {ds}")

        # Commit changes to the database.
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        print("An error occurred while connecting to the Postgres DB instance:", error, sep="\n")

    finally:
        # Close the cursor and connection objects.
        cur.close()
        conn.close()
