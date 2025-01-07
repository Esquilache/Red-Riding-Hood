import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env


def get_db_connection():
    """Establishes and returns a database connection."""
    try:
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        print("Database connection successful.")
        return db
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None


def create_infractions_table():
    """Creates the infractions table if it doesn't already exist."""
    db = get_db_connection()
    if db is None:
        print("Failed to create the table due to a database connection error.")
        return

    try:
        cursor = db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS infractions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id BIGINT NOT NULL,
                guild_id BIGINT NOT NULL,
                moderator_id BIGINT NOT NULL,
                infraction_type VARCHAR(50),
                reason TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        db.commit()
        print("Infractions table created or already exists.")
    except mysql.connector.Error as err:
        print(f"Error creating infractions table: {err}")
    finally:
        db.close()


def log_infraction(user_id, guild_id, moderator_id, infraction_type, reason):
    """Logs an infraction in the database."""
    db = get_db_connection()
    if db is None:
        print("Failed to log the infraction due to a database connection error.")
        return

    try:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO infractions (user_id, guild_id, moderator_id, infraction_type, reason)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, guild_id, moderator_id, infraction_type, reason))
        db.commit()
        print(f"Infraction logged: {infraction_type} for user {user_id}")
    except mysql.connector.Error as err:
        print(f"Error logging infraction: {err}")
    finally:
        db.close()


def get_infractions(member_id, guild_id):
    """Fetches infractions for a specific member in a guild."""
    db = get_db_connection()
    if db is None:
        print("Failed to fetch infractions due to a database connection error.")
        return []

    try:
        cursor = db.cursor(dictionary=True)  # Use dictionary=True for better readability
        cursor.execute("""
            SELECT infraction_type, reason, timestamp 
            FROM infractions 
            WHERE user_id = %s AND guild_id = %s
        """, (member_id, guild_id))
        rows = cursor.fetchall()
        print(f"Fetched {len(rows)} infractions for user {member_id} in guild {guild_id}.")
        return rows
    except mysql.connector.Error as err:
        print(f"Error fetching infractions: {err}")
        return []
    finally:
        db.close()
      