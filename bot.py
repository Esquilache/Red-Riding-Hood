import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import game
import commands
import donations

# Load environment variables from .env file
load_dotenv()

# Bot token from the .env file
TOKEN = os.getenv('BOT_TOKEN')

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True  # For reading messages

bot = commands.Bot(command_prefix="r!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} ({bot.user.id})")
    # Load any startup data or announcements here

@bot.event
async def on_message(message):
    # Ensure bot doesn't reply to itself
    if message.author == bot.user:
        return
    await bot.process_commands(message)

# Load the commands from the other file
bot.add_cog(commands.Commands(bot))

# Run the bot using the token from the .env file
bot.run(TOKEN)
