import json
import requests
from datetime import datetime

from glom import glom, Coalesce
import pandas as pd
import boto3


# Set the API endpoint and token
# url = "http://localhost:3000/api/user/allusers?start_day=2022-07-27&end_day=2022-07-28"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImlkIjoiNjNjODY1ZjM1M2JkZjgyMGY5MjgxNjRjIn0sImlhdCI6MTY3OTM1ODE3N30.krlGV2QiC_KwGcVW38TrlszIPDnb6RSX_ML1Kt206YA"


# Define the function to fetch data from the API and save it to a file
def _fetch_mongo_api_to_json(users_url, extracted_path, **kwargs):
    # Getting the context of the task
    ds = kwargs["ds"]
    year_start, month_start, day_start, hour_start, *_start = kwargs[
        "data_interval_start"
    ].timetuple()
    year_end, month_end, day_end, hour_end, *_end = kwargs[
        "data_interval_end"
    ].timetuple()

    print(f"extracted_path: {extracted_path}")
    print(f"users_url: {users_url}")

    # Set the headers with the token
    headers = {"x-auth-token": token}

    # Url API for the CRM users_url
    # users_url = f"http://192.168.0.13:3000/api/user/allusers?start_day={year_start}-{month_start}-{day_start}&end_day={year_end}-{month_end}-{day_end}"
    # users_url = f"http://192.168.0.13:3000/api/user/allusers?start_day=2022-07-27&end_day=2022-07-28"

    all_items = []

    # Send the GET request to the API with the headers
    response = requests.get(users_url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        all_items.extend(response.json())

    # Save the response content to a file.
    with open(extracted_path, "w") as _file:
        # Write the list of dictionaries to a JSON file
        json.dump(all_items, _file)

    print(f"JSON file created successfully ({ds}).")


# Define the function to read the JSON file and transform it into a Pandas DataFrame
def _transform_users_to_csv(extracted_path, transformed_path, **kwargs):
    # Getting the context of the task
    ds = kwargs["ds"]

    print(f"extracted_path: {extracted_path}")
    print(f"transformed_path: {transformed_path}")

    # Read the JSON file into a Pandas DataFrame
    # load data using Python JSON module
    with open(extracted_path, "r") as _file:
        data = json.loads(_file.read())

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
            "profileImg_url": (Coalesce("profileImg_url", default=""), str),
            "licenseImg_url": (Coalesce("licenseImg_url", default=""), str),
            "insuranceImg_url": (Coalesce("insuranceImg_url", default=""), str),
            "date": (
                "date",
                lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%f%z").strftime(
                    "%Y-%m-%d"
                ),
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

    # Use glom to extract the flattened data
    df = pd.DataFrame(glom(data, expr))

    # Save the Pandas DataFrame to a file
    df.to_csv(transformed_path, index=False)

    print(f"CSV file created successfully ({ds}).")


# Define the function to fetch data from the API and save it to a file
def _check_the_bucket_connection(
    aws_access_key_id, aws_secret_access_key, endpoint_url, **kwargs
):
    # Getting the context of the task
    ds = kwargs["ds"]
    linode_obj_config = {
        "aws_access_key_id": aws_access_key_id,
        "aws_secret_access_key": aws_secret_access_key,
        "endpoint_url": endpoint_url,
    }

    client = boto3.client("s3", **linode_obj_config)
    response = client.list_buckets()
    for bucket in response["Buckets"]:
        print(bucket["Name"])

    print(f"Connection successfully ({ds}).")
