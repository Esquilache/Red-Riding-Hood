import discord  # Ensure discord is imported
from discord.ext import commands

class Social(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def welcome(self, ctx, user: discord.User):
        """Send a welcome message to a user."""
        await ctx.send(f"Welcome to the server, {user.mention}!")

    @commands.command()
    async def giveaway(self, ctx, prize: str, duration: int):
        """Create a giveaway with a specified prize and duration."""
        await ctx.send(f"Giveaway for {prize} starting now! Duration: {duration} minutes")

async def setup(bot):
    await bot.add_cog(Social(bot))
