import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
import logging
from db import create_infractions_table

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s]: %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('COMMAND_PREFIX', "r!")  # Command prefix with dynamic configuration

# Configure intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Correct attribute for member intents

# Set up the bot
bot = commands.Bot(command_prefix=PREFIX, intents=intents)


@bot.event
async def on_ready():
    """Event triggered when the bot is ready."""
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    logging.info(f'Bot is ready: {bot.user.name} ({bot.user.id})')

    # Ensure database table exists
    create_infractions_table()

    # Load cogs
    for cog in os.listdir('./cogs'):
        if cog.endswith('.py') and os.path.isfile(f'./cogs/{cog}'):
            try:
                await bot.load_extension(f'cogs.{cog[:-3]}')
                print(f'Loaded cog: {cog}')
                logging.info(f'Loaded cog: {cog}')
            except Exception as e:
                print(f'Failed to load cog {cog}: {e}')
                logging.error(f'Failed to load cog {cog}: {e}')


async def main():
    """Main asynchronous entry point."""
    async with bot:
        await bot.start(TOKEN)


# Run the bot
if __name__ == "__main__":
    asyncio.run(main())
    