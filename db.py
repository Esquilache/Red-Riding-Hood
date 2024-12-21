import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database credentials from the .env file
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')

def connect_to_db():
    """Connect to the database using credentials from .env file."""
    try:
        db_connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )
        print(f"Connected to MySQL database: {db_name}")
        return db_connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def close_db_connection(db_connection):
    """Close the database connection."""
    if db_connection.is_connected():
        db_connection.close()
        print("Database connection closed.")
