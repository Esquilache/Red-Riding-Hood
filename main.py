import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio  # Import asyncio for async support

# Load environment variables from .env file
load_dotenv()

# Get the bot token from the environment variable
TOKEN = os.getenv("DISCORD_TOKEN")

# Create bot instance with prefix 'r.'
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent
intents.members = True  # Enable member intent if needed for welcome or role management

bot = commands.Bot(command_prefix="r.", intents=intents)

# Event when bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    # Load modules after the bot is ready
    await load_modules()

# Function to dynamically load a module
@bot.command()
async def load(ctx, module: str):
    try:
        await bot.load_extension(f'modules.{module}')
        await ctx.send(f'{module} module loaded successfully!')
    except Exception as e:
        await ctx.send(f'Error loading module {module}: {e}')

# Function to dynamically unload a module
@bot.command()
async def unload(ctx, module: str):
    try:
        await bot.unload_extension(f'modules.{module}')
        await ctx.send(f'{module} module unloaded successfully!')
    except Exception as e:
        await ctx.send(f'Error unloading module {module}: {e}')

# Automatically load all modules in the 'modules' directory
async def load_modules():
    for filename in os.listdir('./modules'):
        if filename.endswith('.py'):
            module_name = filename[:-3]
            try:
                await bot.load_extension(f'modules.{module_name}')
                print(f'{module_name} module loaded.')
            except Exception as e:
                print(f'Failed to load {module_name}: {e}')

# Run the bot with the token from .env
bot.run(TOKEN)
