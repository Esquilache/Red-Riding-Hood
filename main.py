import discord
import mysql.connector
import os
from dotenv import load_dotenv
from db import setup_db, insert_test_data, test_data_retrieval

# Load environment variables from .env file
load_dotenv()

# Now get the bot token from the environment
bot_token = os.getenv('BOT_TOKEN')

# Debugging line to check if the token is loaded correctly
if not bot_token:
    print("Error: BOT_TOKEN not found in .env file!")
else:
    print(f"Bot token loaded: {bot_token}")

# Discord Client Setup
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# Database Connection
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

@client.event
async def on_ready():
    """Bot is ready and connected to Discord and database."""
    print(f'Logged in as {client.user}')
    
    # Connect to database
    db_connection = connect_to_db()

    if db_connection:
        print("Bot is ready and database is connected!")

        # Setup DB (Create tables if needed)
        setup_db(db_connection)

        # Test inserting data
        insert_test_data(db_connection)

        # Test retrieving data
        test_data_retrieval(db_connection)

    else:
        print("Failed to connect to the database.")

# Setup bot token
bot_token = os.getenv('DISCORD_BOT_TOKEN')
client.run(bot_token)
