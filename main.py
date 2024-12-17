import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables from .env file
load_dotenv()

# Get the bot token from the environment variable
TOKEN = os.getenv("DISCORD_TOKEN")

# Database imports
from db import setup_db, test_db_connection

# Create bot instance with prefix 'r.'
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent
intents.members = True  # Enable member intent if needed for welcome or role management

bot = commands.Bot(command_prefix="r.", intents=intents)

# Event when bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    
    # Test database connection and setup
    if test_db_connection():
        print("Database is connected successfully.")
        await setup_db()  # Set up the database and tables
        await insert_test_data()  # Insert test data to verify everything is working
        await test_data_retrieval()  # Retrieve test data to ensure it's working
        
    # Other bot initialization logic...
    
    print("Bot is ready and database is connected!")

# Start the bot with the token
bot.run(TOKEN)
