import os

import psycopg2

# Access environment variables from the .env file.
DB_USERNAME = os.environ.get("DB_USERNAME")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")


def test_db_connection():
    # Try to establish a connection to the database
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USERNAME,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
        # If the connection is successful, assert that the cursor object is not None
        assert conn.cursor() is not None
    except Exception as e:
        # If the connection fails, raise an AssertionError with an appropriate message
        raise AssertionError(f"Failed to connect to the database: {e}")
    finally:
        # Close the connection in the finally block to ensure proper resource cleanup
        conn.close() if conn else None
