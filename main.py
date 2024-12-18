import discord
from discord.ext import commands
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

# Discord Bot Setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='r.', intents=intents)

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

@bot.event
async def on_ready():
    """Bot is ready and connected to Discord and database."""
    print(f'Logged in as {bot.user}')
    
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

    # Load all cogs on startup (await the asynchronous method)
    try:
        await bot.load_extension('modules.moderation')
        await bot.load_extension('modules.social')
        await bot.load_extension('modules.status')
        print("Cogs loaded successfully.")
    except Exception as e:
        print(f"Error loading cogs: {e}")

# Load cog command
@bot.command()
async def load(ctx, extension):
    """Load a cog dynamically."""
    try:
        await bot.load_extension(f"modules.{extension}")
        await ctx.send(f"Cog {extension} loaded successfully!")
    except Exception as e:
        await ctx.send(f"Error loading cog {extension}: {e}")

# Unload cog command
@bot.command()
async def unload(ctx, extension):
    """Unload a cog dynamically."""
    try:
        await bot.unload_extension(f"modules.{extension}")
        await ctx.send(f"Cog {extension} unloaded successfully!")
    except Exception as e:
        await ctx.send(f"Error unloading cog {extension}: {e}")

# Run the bot
bot.run(bot_token)
