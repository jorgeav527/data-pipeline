import json
import os
from datetime import datetime, timezone

import pandas as pd
import requests
from glom import Coalesce, glom

RDSTATION_API_TOKEN = os.environ.get("RDSTATION_API_TOKEN")


# Define the function to fetch data from the API and save it to a file
def _fetch_rdstudioapicmr_contacts_to_json(extracted_path, **kwargs):
    # Getting the context of the task
    ds = kwargs["ds"]
    year_start, month_start, day_start, hour_start, *_start = kwargs["data_interval_start"].timetuple()
    year_end, month_end, day_end, hour_end, *_end = kwargs["data_interval_end"].timetuple()

    print(f"extracted_path: {extracted_path}")

    # Url API for the CRM users
    contacts_url = f"https://crm.rdstation.com/api/v1/contacts?token={RDSTATION_API_TOKEN}"
    params = {"page": 1}
    all_items = []

    response = requests.get(contacts_url)

    # Check if the request was successful
    if response.status_code == 200:
        while True:
            response = requests.get(contacts_url, params=params)
            data = response.json()
            all_items.extend(data["contacts"])
            if data["has_more"]:
                params["page"] += 1
            else:
                break

    # define the datetime range we want to filter by
    # start_date = datetime(year_start, month_start, day_start, tzinfo=timezone.utc)
    # end_date = datetime(year_end, month_end, day_end, tzinfo=timezone.utc)
    start_date = datetime(2022, 10, 4, tzinfo=timezone.utc)
    end_date = datetime(2022, 10, 5, tzinfo=timezone.utc)

    # filter the list of dictionaries by datetime
    filtered_data = [
        record
        for record in all_items
        if start_date <= datetime.fromisoformat(record["created_at"]).astimezone(timezone.utc) < end_date
    ]
    # Save the response content to a file.
    with open(extracted_path, "w") as _file:
        # Write the list of dictionaries to a JSON file
        json.dump(filtered_data, _file)

    print(f"JSON file created successfully ({ds}).")


# Define the function to read the JSON file and transform it into a Pandas DataFrame
def _transform_contacts_to_csv(extracted_path, transformed_path, **kwargs):
    # Getting the context of the task
    ds = kwargs["ds"]
    year_start, month_start, day_start, hour_start, *_start = kwargs["data_interval_start"].timetuple()
    year_end, month_end, day_end, hour_end, *_end = kwargs["data_interval_end"].timetuple()

    print(f"extracted_path: {extracted_path}")
    print(f"transformed_path: {transformed_path}")

    # Read the JSON file into a Pandas DataFrame
    # load data using Python JSON module
    with open(extracted_path, "r") as _file:
        data = json.loads(_file.read())

    expr = (
        [
            {
                "_id": "_id",
                "title": (Coalesce("title", default=""), str),
                "facebook": (Coalesce("facebook", default=""), str),
                "linkedin": (Coalesce("linkedin", default=""), str),
                "skype": (Coalesce("skype", default=""), str),
                "created_at": (
                    "created_at",
                    lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%Y-%m-%d"),
                ),
                "updated_at": (
                    "updated_at",
                    lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%Y-%m-%d"),
                ),
                "email": ("emails", ["email"]),
                "phone": ("phones", ["phone"]),
            },
        ],
    )

    # Use glom to extract the flattened data
    df = pd.DataFrame(glom(data, expr))

    # Save the Pandas DataFrame to a file
    df.to_csv(transformed_path, index=False)

    print(f"CSV file created successfully ({ds}).")
