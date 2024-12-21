import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from db import connect_to_db
from setup_db import initialize_tables

# Load environment variables from .env file
load_dotenv()

# Initialize intents
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent
intents.members = True  # Enable member-related events

# Create bot instance
bot = commands.Bot(command_prefix='r.', intents=intents)

# Connect to the database
db_connection = connect_to_db()

@bot.event
async def on_ready():
    """Event that runs when the bot is ready."""
    print(f"Bot logged in as {bot.user}")
    # Initialize the database tables if they are not already set up
    initialize_tables()

    # Load the cogs
    try:
        await bot.load_extension('modules.moderation')
        await bot.load_extension('modules.social')
        await bot.load_extension('modules.status')
        print("Cogs loaded successfully.")
    except Exception as e:
        print(f"Error loading cogs: {e}")

@bot.event
async def on_member_join(member):
    """Handle a new member joining."""
    print(f"{member} has joined the server.")

@bot.command()
async def test(ctx):
    """A simple command to test the bot."""
    await ctx.send("Bot is running successfully!")

# Run the bot using the token from the .env file
bot_token = os.getenv("BOT_TOKEN")
if bot_token:
    bot.run(bot_token)
else:
    print("Bot token not found in .env file.")
