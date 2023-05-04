import json
import os
import time
from datetime import datetime

import pandas as pd
import requests
from glom import Coalesce, glom


def _check_mongodb_api_connection(api_token, url):
    """
    Check the MongoDB API connection by sending a GET request to the specified URL with headers containing the API token.
    This function will try to connect to the API every 60 seconds until it succeeds or until the timeout of 120 seconds is reached.

    Args:
    - api_token (string): The API token to authenticate the request.
    - url (string): The URL endpoint to check the connection against.

    Returns:
    - True if the connection was successful, False otherwise.
    """  # noqa: E501
    # To debug the parameters.
    print(f"api_token: {api_token}")
    print(f"url: {url}")

    headers = {"x-auth-token": api_token}
    timeout = 30  # Seconds.
    poke_interval = 15  # Seconds.
    start_time = time.time()  # Record the start time of the script execution.

    # Continuously send requests until a 200 response code is received or the timeout is reached.
    while True:
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            if response.status_code == 200:
                return True
        except Exception as error:
            # If an error occurs (e.g. connection refused), ignore it and continue the loop.
            print("An error occurred while connecting to the API:", error, sep="\n")
            pass

        # If the timeout has been reached, return False to indicate failure.
        if time.time() - start_time > timeout:
            return False

        # Pause for the specified interval before sending the next request.
        time.sleep(poke_interval)


def _fetch_mongo_api_to_json(extracted_path, api_token, users_url, bucket_key_path, client, **kwargs):
    """
    Sending a GET request to the specified URL (/api/user/allusers) with headers and (?start_day=<YYYY-MM-DD>&end_day=<YYYY-MM-DD>) parameters.
    This function will retrieve data from the API on a daily basis and save it in YYYY-MM-DD.json format into a S3 bucket.

    Args:
    - extracted_path (string): The temporary path (bucket/extracted_data/*.json) where the data will be saved.
    - api_token (string): The API token to authenticate the request.
    - users_url (string): The URL endpoint to fetch the data.
    - bucket_key_path (string): The actual bucket path where the extracted data will be saved.
    - client (object): Call the boto3 client to connect to the bucket.
    **kwargs:
    - kwargs["ds"] (dictionary): The day that the task ends up happening.

    Returns:
    - A string "JSON file was successfully added to the bucket as at ({ds}.json).". If the data was succesfully extracted.
    """  # noqa: E501

    # Getting some information from the task's context.
    ds = kwargs["ds"]

    # To debug the parameters.
    print(f"extracted_path: {extracted_path}")
    print(f"api_token: {api_token}")
    print(f"users_url: {users_url}")
    print(f"bucket_key_path: {bucket_key_path}")

    # Set the headers with the token.
    headers = {"x-auth-token": api_token}

    # Make an empty list to append the data to.
    all_items = []

    # Send the GET request to the API with the headers.
    response = requests.get(users_url, headers=headers)

    # Check if the request was successful.
    if response.status_code == 200:
        all_items.extend(response.json())

    print(f"response:: {response}")

    # Save the response content to a temporaly file.
    with open(extracted_path, "w") as _file:
        # Write the list of dictionaries to a JSON file.
        json.dump(all_items, _file)

    # Call the S3 bucket client to save a file.
    client.upload_file(
        Filename=extracted_path,
        Bucket="roadr-data-lake",
        Key=bucket_key_path,
        ExtraArgs={"ACL": "public-read"},
    )

    # Delete the local file.
    os.remove(extracted_path)

    print(f"JSON file successfully added to the bucket at ({ds}.json).")


def _transform_users_to_csv(extracted_url, transformed_path, bucket_key_path, client, **kwargs):
    """
    Sending a GET request to get the extracted daily YYYY-MM-DD.json file from the bucket file.
    This function should extract the YYYY-MM-DD.json data file and then transform and convert it to a more structured CVS file format.
    Only selected fields will be saved.

    Args:
    - extracted_url (string): The actual bucket path where the extracted data will be pulled.
    - transformed_path (string): The temporary path (bucket/transformed_data/*.csv) where the data will be saved.
    - bucket_key_path (string): The actual bucket path where the transformed data will be saved.
    - client (object): Call the boto3 client to connect to the bucket.
    **kwargs:
    - kwargs["ds"] (dictionary): The day that the task ends up happening.

    Returns:
    - A string "CSV file was successfully added to the bucket as at ({ds}.csv).". If the data was succesfully transformed.
    """  # noqa: E501

    # Getting the context of the task
    ds = kwargs["ds"]

    # To debug the parameters.
    print(f"extracted_url: {extracted_url}")
    print(f"transformed_path: {transformed_path}")
    print(f"bucket_key_path: {bucket_key_path}")

    # Read the JSON file with a Pandas DataFrame.
    data = pd.read_json(
        extracted_url,
        orient="records",
        typ="series",
    )

    # Make a glom expression that converts and flattens a JSON data file to a CSV data file.
    expr = [
        {
            "_id": "_id",
            "name": (Coalesce("name", default=""), str),
            "email": (Coalesce("email", default=""), str),
            "about": (Coalesce("about", default=""), str),
            "phoneNumber": (Coalesce("phoneNumber", default=""), str),
            "criminalStatus": (Coalesce("criminalStatus", default=""), str),
            "isClient": (Coalesce("isClient", default=False), bool),
            "IsSpecialist": (Coalesce("IsSpecialist", default=False), bool),
            "isValidCertification": (
                Coalesce("isValidCertification", default=False),
                bool,
            ),
            "isActive": (Coalesce("isActive", default=False), bool),
            "isDeleted": (Coalesce("isDeleted", default=False), bool),
            "registerType": (Coalesce("registerType", default=""), str),
            "profileImg_url": (Coalesce("profileImg.uri", default=""), str),
            "licenseImg_url": (Coalesce("licenseImg.uri", default=""), str),
            "insuranceImg_url": (Coalesce("insuranceImg.uri", default=""), str),
            "date": (
                "date",
                lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%Y-%m-%d"),
            ),
            "__v": (Coalesce("__v", default=0), int),
            # Refuel
            "hasServices_refuel_name": (
                Coalesce("hasServices.refuel.name", default=""),
                str,
            ),
            "hasServices_refuel_type": (
                Coalesce("hasServices.refuel.type", default=""),
                str,
            ),
            "hasServices_refuel_isVerified": (
                Coalesce("hasServices.refuel.isVerified", default=False),
                bool,
            ),
            "hasServices_refuel_isApproved": (
                Coalesce("hasServices.refuel.isApproved", default=False),
                bool,
            ),
            # Tire change
            "hasServices_tire_change_name": (
                Coalesce("hasServices.tire_change.name", default=""),
                str,
            ),
            "hasServices_tire_change_type": (
                Coalesce("hasServices.tire_change.type", default=""),
                str,
            ),
            "hasServices_tire_change_isVerified": (
                Coalesce("hasServices.tire_change.isVerified", default=False),
                bool,
            ),
            "hasServices_tire_change_isApproved": (
                Coalesce("hasServices.tire_change.isApproved", default=False),
                bool,
            ),
            "hasServices_tire_change_certificate_uri": (
                Coalesce("hasServices.tire_change.certificate.uri", default=""),
                str,
            ),
            # Jump
            "hasServices_jump_name": (
                Coalesce("hasServices.jump.name", default=""),
                str,
            ),
            "hasServices_jump_type": (
                Coalesce("hasServices.jump.type", default=""),
                str,
            ),
            "hasServices_jump_isVerified": (
                Coalesce("hasServices.jump.isVerified", default=False),
                bool,
            ),
            "hasServices_jump_isApproved": (
                Coalesce("hasServices.jump.isApproved", default=False),
                bool,
            ),
            "hasServices_jump_certificate_uri": (
                Coalesce("hasServices.jump.certificate.uri", default=""),
                str,
            ),
            # Unlock
            "hasServices_unlock_name": (
                Coalesce("hasServices.unlock.name", default=""),
                str,
            ),
            "hasServices_unlock_type": (
                Coalesce("hasServices.unlock.type", default=""),
                str,
            ),
            "hasServices_unlock_isVerified": (
                Coalesce("hasServices.unlock.isVerified", default=False),
                bool,
            ),
            "hasServices_unlock_isApproved": (
                Coalesce("hasServices.unlock.isApproved", default=False),
                bool,
            ),
            "hasServices_unlock_certificate_uri": (
                Coalesce("hasServices.unlock.certificate.uri", default=""),
                str,
            ),
            "company_id": (Coalesce("company.company_id", default=""), str),
            "company_status": (Coalesce("company.status", default=""), str),
        }
    ]

    # Use glom to extract the flattened data and transform it into a dataframe.
    df = pd.DataFrame(glom(data, expr))

    # Save the Pandas DataFrame to a CSV file.
    df.to_csv(transformed_path, index=False)

    # Call the S3 bucket client to save a file.
    client.upload_file(
        Filename=transformed_path,
        Bucket="roadr-data-lake",
        Key=bucket_key_path,
        ExtraArgs={"ACL": "public-read"},
    )

    # Delete the local file
    os.remove(transformed_path)

    print(f"CSV file was successfully added to the bucket at ({ds}.csv).")
