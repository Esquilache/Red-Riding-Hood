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

def setup_db(db_connection):
    """Set up the database by creating necessary tables if they don't exist."""
    cursor = db_connection.cursor()

    # Example table creation query (create a test_table for demonstration purposes)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS test_table (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL
    );
    """)
    db_connection.commit()
    print("Database and table setup successful!")

def insert_test_data(db_connection):
    """Insert test data into the database."""
    cursor = db_connection.cursor()

    # Insert data into the test_table
    cursor.execute("INSERT INTO test_table (name) VALUES ('Test User')")
    db_connection.commit()
    print("Test data inserted successfully!")

def test_data_retrieval(db_connection):
    """Retrieve and print test data from the database."""
    cursor = db_connection.cursor()

    # Fetch all rows from test_table
    cursor.execute("SELECT * FROM test_table")
    result = cursor.fetchall()
    
    # Print out all rows from the result
    for row in result:
        print(row)

# Close the DB connection (optional)
def close_db_connection(db_connection):
    """Close the database connection."""
    if db_connection.is_connected():
        db_connection.close()
        print("Database connection closed.")
