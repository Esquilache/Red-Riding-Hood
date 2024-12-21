import discord
from discord.ext import commands
import random
import re
from datetime import timedelta
from discord.utils import sleep_until

class Social(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.giveaway_channel = None  # Stores the giveaway channel

    @commands.command()
    async def setchannel(self, ctx, channel: discord.TextChannel):
        """Set the default giveaway channel."""
        # Permission check
        if not ctx.author.permissions_in(ctx.channel).manage_guild:
            await ctx.send("You don't have permission to set the giveaway channel.")
            return

        # Set the giveaway channel
        self.giveaway_channel = channel
        await ctx.send(f"Giveaway channel has been set to {channel.mention}.")

    @commands.command()
    async def giveaway(self, ctx, prize: str, duration: str):
        """Start a giveaway with a specified prize and duration."""
        # Validate that a giveaway channel is set
        if self.giveaway_channel is None:
            await ctx.send("No giveaway channel has been set. Use `r.giveaway setchannel #channel` first.")
            return

        # Parse duration
        duration_seconds = self.parse_duration(duration)
        if duration_seconds is None:
            await ctx.send("Invalid time format. Use format like `1d 2h 30m`.")
            return

        # Post the giveaway message in the set giveaway channel
        giveaway_msg = await self.giveaway_channel.send(
            f"🎉 **GIVEAWAY TIME** 🎉\nPrize: {prize}\nReact with 🎉 to enter!\nTime remaining: {duration}!"
        )
        await giveaway_msg.add_reaction("🎉")

        # Wait for the giveaway to end and pick a winner
        await self.wait_for_giveaway_end(giveaway_msg, duration_seconds, prize)

    def parse_duration(self, duration: str):
        """Parse duration string into seconds."""
        time_regex = re.compile(r"(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?")
        match = time_regex.match(duration)
        if not match:
            return None

        days, hours, minutes = match.groups()
        return timedelta(
            days=int(days) if days else 0,
            hours=int(hours) if hours else 0,
            minutes=int(minutes) if minutes else 0,
        ).total_seconds()

    async def wait_for_giveaway_end(self, message, duration_seconds, prize):
        """Wait for giveaway to end and pick a winner."""
        await sleep_until(message.created_at + timedelta(seconds=duration_seconds))

        # Check for reactions
        reaction = discord.utils.get(message.reactions, emoji="🎉")
        if reaction:
            users = await reaction.users().flatten()
            users = [user for user in users if not user.bot]

            if users:
                winner = random.choice(users)
                await message.channel.send(f"🎉 Congratulations {winner.mention}, you won **{prize}**!")
            else:
                await message.channel.send("No participants, giveaway has been canceled.")
        else:
            await message.channel.send("No reactions received, giveaway canceled.")

async def setup(bot):
    await bot.add_cog(Social(bot))
