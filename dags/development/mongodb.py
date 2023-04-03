import json
import pandas as pd
import requests
from datetime import datetime, timezone

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# Set the MongoDB database connections.
MONGO_URL = "mongodb+srv://roadr_dev:7juzcxuvMpMlyfHO@devcluster.8igvo.mongodb.net/?retryWrites=true&w=majority"
# HOST = "lin-18457-6369-pgsql-primary.servers.linodedb.net"
# DATABASE = "postgres"
# USER = "linpostgres"
# PASSWORD = "zB9DpFxA-CpBD5Ws"
# PORT = 5432


# Check connection with the mongo db.
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


# Define the function to read the JSON file and transform it into a Pandas DataFrame
def _transform_users_save():
    # Read the JSON file into a Pandas DataFrame
    # load data using Python JSON module
    with open("bucket/extracted_data/mongodb_users.json", "r") as _file:
        data = json.loads(_file.read())

    # Save the Pandas DataFrame to a file
    df = pd.json_normalize(data, sep="_")
    df.to_csv("bucket/transformed_data/mongodb_users.csv", index=False)
