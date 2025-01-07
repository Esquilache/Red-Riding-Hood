import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional

class Boosters(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.booster_channel_id = None  # Store the booster channel ID
        self.boosters = []  # List to store booster data
        self.custom_message = (
            "🎉✨ {user}, thank you for boosting **{server}**! Your support is magical! ✨🎉"
        )

    @commands.group(name='booster', invoke_without_command=True)
    async def booster(self, ctx):
        """Main command group for managing server boosters."""
        await ctx.send("Available subcommands: showall, set channel, simulate, add, remove, clear, setmessage")

    @booster.command(name='showall')
    async def showall(self, ctx):
        """Shows a list of server boosters."""
        if not self.boosters:
            await ctx.send("No boosters found.")
            return
        embed = discord.Embed(
            title="Server Boosters",
            description="\n".join([f"✨ {booster}" for booster in self.boosters]),
            color=0xFFD700  # Gold color for boosting
        )
        await ctx.send(embed=embed)

    @booster.command(name='set')
    @commands.has_permissions(administrator=True)
    async def set_channel(self, ctx, channel: discord.TextChannel):
        """Sets the channel for booster announcements."""
        self.booster_channel_id = channel.id
        await ctx.send(f"Booster announcements will now be sent in {channel.mention}")

    @booster.command(name='simulate')
    async def simulate(self, ctx):
        """Simulates a boosting event."""
        if not self.booster_channel_id:
            await ctx.send("Booster channel is not set. Use `r!booster set channel #channel` first.")
            return
        channel = self.bot.get_channel(self.booster_channel_id)
        if not channel:
            await ctx.send("Booster channel is invalid. Please set it again.")
            return
        message = self.custom_message.format(user=ctx.author.mention, server=ctx.guild.name)
        await channel.send(message)

    @booster.command(name='add')
    async def add(self, ctx, member: discord.Member):
        """Manually adds a user to the booster list."""
        self.boosters.append(member.mention)
        await ctx.send(f"{member.mention} has been added to the booster list.")

    @booster.command(name='remove')
    async def remove(self, ctx, member: discord.Member):
        """Removes a user from the booster list."""
        if member.mention in self.boosters:
            self.boosters.remove(member.mention)
            await ctx.send(f"{member.mention} has been removed from the booster list.")
        else:
            await ctx.send(f"{member.mention} is not in the booster list.")

    @booster.command(name='clear')
    @commands.has_permissions(administrator=True)
    async def clear(self, ctx):
        """Clears the booster list."""
        self.boosters.clear()
        await ctx.send("Booster list has been cleared.")

    @booster.command(name='setmessage')
    @commands.has_permissions(administrator=True)
    async def setmessage(self, ctx, *, message: str):
        """Sets a custom thank-you message for boosting."""
        self.custom_message = message
        await ctx.send("Custom thank-you message has been updated.")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Detects when a user starts boosting and sends a thank-you message."""
        if not before.premium_since and after.premium_since:
            if self.booster_channel_id:
                channel = self.bot.get_channel(self.booster_channel_id)
                if channel:
                    message = self.custom_message.format(
                        user=after.mention, server=after.guild.name
                    )
                    await channel.send(message)

async def setup(bot):
    await bot.add_cog(Boosters(bot))
    