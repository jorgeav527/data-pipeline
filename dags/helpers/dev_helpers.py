import os
import requests

import pandas as pd
import psycopg2


# Define a function that reads the CSV file and converts it to a SQL file
def _create_sql_file(
    client, transformed_path, loaded_path, table_name, columns, **kwargs
):
    # Getting the context of the task
    ds = kwargs["ds"]
    print(f"transformed_path: {transformed_path}")
    print(f"loaded_path: {loaded_path}")
    # Read the CSV file into a Pandas dataframe
    url = f"https://roadr-data-lake.us-southeast-1.linodeobjects.com/transformed_data/mongodb_api/users/{ds}.csv"
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
            file.write(
                "INSERT INTO {} ({}) VALUES ({});\n".format(
                    table_name, ",".join(columns), ",".join(values)
                )
            )
    client.upload_file(
        Filename=loaded_path,
        Bucket="roadr-data-lake",
        Key=f"loaded_data/mongodb_api/users/{ds}.sql",
        ExtraArgs={"ACL": "public-read"},
    )

    # Delete the local file
    os.remove(loaded_path)

    # Print a message indicating that the SQL file has been created
    print("SQL file created successfully.")


def _inject_sql_file_to_postgres(loaded_path):
    print(f"loaded_path: {loaded_path}")

    # Define connection parameters
    conn_params = {
        "host": "lin-18905-6547-pgsql-primary.servers.linodedb.net",
        "database": "postgres",
        "user": "linpostgres",
        "password": "bZu7-UgMYKY7fksN",
        "port": 5432,
    }

    # Open a connection to the database
    conn = psycopg2.connect(**conn_params)
    cursor = conn.cursor()

    # Read the SQL file contents
    url = f"https://roadr-data-lake.us-southeast-1.linodeobjects.com/loaded_data/mongodb_api/users/2023-04-07.sql"
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
    print("SQL file injected successfully.")
