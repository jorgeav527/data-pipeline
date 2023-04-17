import os

import pandas as pd
import psycopg2
import requests

DB_USERNAME = os.environ.get("DB_USERNAME")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")


# Define a function that reads the CSV file and converts it to a SQL file
def _create_sql_file(client, transformed_url, loaded_path, bucket_key_path, table_name, columns, **kwargs):
    # Getting the context of the task
    ds = kwargs["ds"]
    print(f"transformed_url: {transformed_url}")
    print(f"loaded_path: {loaded_path}")
    print(f"bucket_key_path: {bucket_key_path}")
    # Read the CSV file into a Pandas dataframe
    url = transformed_url
    df = pd.read_csv(url)

    # Open the SQL file in write mode
    with open(loaded_path, "w") as file:
        # Iterate over each row in the dataframe
        for index, row in df.iterrows():
            # Build the list of values to insert into the SQL statement
            values = []
            for column in columns:
                # Get the value of the current column for the current row
                value = row[column]

                # Check the data type of the value and format it appropriately
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

            # Write the SQL statement to the file
            file.write("INSERT INTO {} ({}) VALUES ({});\n".format(table_name, ",".join(columns), ",".join(values)))
    client.upload_file(
        Filename=loaded_path,
        Bucket="roadr-data-lake",
        Key=bucket_key_path,
        ExtraArgs={"ACL": "public-read"},
    )

    # Delete the local file
    os.remove(loaded_path)

    # Print a message indicating that the SQL file has been created
    print(f"SQL file created successfully ({ds}).")


def _inject_sql_file_to_postgres(loaded_url, **kwargs):
    # Getting the context of the task
    ds = kwargs["ds"]
    print(f"loaded_url: {loaded_url}")

    # Define connection parameters
    conn_params = {
        "user": DB_USERNAME,
        "password": DB_PASSWORD,
        "host": DB_HOST,
        "port": DB_PORT,
        "database": DB_NAME,
    }

    # Open a connection to the database
    conn = psycopg2.connect(**conn_params)
    cursor = conn.cursor()

    # Read the SQL file contents
    url = loaded_url
    response = requests.get(url)
    # response.raise_for_status()  # raise an exception if the request fails
    sql = response.text
    print("sql", sql)

    # Execute the SQL script
    cursor.execute(sql)

    # Commit changes to the database
    conn.commit()

    # Close the cursor and the connection
    cursor.close()
    conn.close()

    # Print a message indicating that the SQL file has been created
    print(f"SQL file injected successfully ({ds}).")
