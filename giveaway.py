import re
import discord
from discord.ext import commands
import asyncio
from datetime import timedelta
import random  # For selecting random winners

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_giveaways = {}
        self.notifications = {}  # Store users who subscribe to notifications
        self.guild_giveaway_channel = {}  # Store the giveaway channel for each server

    @commands.command(name="set_giveaway_channel")
    @commands.has_permissions(administrator=True)
    async def set_giveaway_channel(self, ctx, channel: discord.TextChannel):
        """Sets the channel where giveaways will be posted."""
        self.guild_giveaway_channel[ctx.guild.id] = channel.id
        await ctx.send(f"Giveaway channel has been set to: {channel.mention}")

    @commands.command(name="giveaway_start")
    async def giveaway_start(self, ctx, time: str, winners: int, emoji: str, prize: str, image_url: str = None):
        """Starts a giveaway with the specified parameters."""
        try:
            print(f"Received input: time={time}, winners={winners}, emoji={emoji}, prize={prize}")

            # Parse time
            duration = self.parse_time(time)
            if duration is None:
                return await ctx.send("Invalid time format. Use `XdXhXm` (e.g., `1d2h30m`).")

            print(f"Parsed duration: {duration} seconds")

            # Validate winners
            if winners < 1:
                return await ctx.send("There must be at least 1 winner.")

            # Allow for multiple emojis separated by commas
            emojis = emoji.split(',')
            if len(emojis) > winners:
                return await ctx.send("You can't have more emojis than winners!")

            # Get the giveaway channel (either the set channel or the current channel)
            giveaway_channel = ctx.channel
            if ctx.guild.id in self.guild_giveaway_channel:
                giveaway_channel = self.bot.get_channel(self.guild_giveaway_channel[ctx.guild.id])
                if not giveaway_channel:
                    return await ctx.send("Invalid giveaway channel. Please ask an admin to set it again.")

            # Create giveaway embed with optional prize image
            embed = discord.Embed(
                title="🎉 Giveaway! 🎉",
                description=(
                    f"**Prize:** {prize}\n"
                    f"**React with {emoji} to enter!**\n"
                    f"**Time Remaining:** {time}\n"
                    f"**Winners:** {winners}"
                ),
                color=discord.Color.green(),
            )
            if image_url:
                embed.set_image(url=image_url)

            embed.set_footer(text="Good luck!")

            # Send the giveaway message in the selected channel
            message = await giveaway_channel.send(embed=embed)

            # Add multiple reactions
            for emj in emojis:
                await message.add_reaction(emj)

            # Store giveaway details
            self.active_giveaways[message.id] = {
                "channel": giveaway_channel.id,
                "duration": duration,
                "winners": winners,
                "emojis": emojis,  # Store the emojis list
                "prize": prize,
            }

            # Wait for the duration and select winners
            await asyncio.sleep(duration)
            await self.end_giveaway(message.id)
        except Exception as e:
            print(f"Error in giveaway_start: {e}")
            await ctx.send("An error occurred while starting the giveaway.")

    def parse_time(self, time_str: str):
        """Parses a time string into seconds."""
        pattern = r"((?P<days>\d+)d)?((?P<hours>\d+)h)?((?P<minutes>\d+)m)?"
        match = re.match(pattern, time_str)
        if not match:
            return None

        time_data = {key: int(value) if value else 0 for key, value in match.groupdict().items()}
        delta = timedelta(days=time_data["days"], hours=time_data["hours"], minutes=time_data["minutes"])
        return int(delta.total_seconds())

    async def end_giveaway(self, message_id: int):
        """Ends the giveaway and selects winners."""
        details = self.active_giveaways.get(message_id)
        if not details:
            return

        channel = self.bot.get_channel(details["channel"])
        if not channel:
            return

        message = await channel.fetch_message(message_id)
        if not message:
            return

        # Retrieve all users who reacted with the specified emoji
        reaction = discord.utils.get(message.reactions, emoji=details["emojis"][0])
        if reaction is None:
            return await channel.send("No valid reactions found for the giveaway.")

        users = []
        async for user in reaction.users():
            if not user.bot:  # Exclude the bot itself
                users.append(user)

        # Select winners
        if len(users) < details["winners"]:
            return await channel.send("Not enough participants for the giveaway.")
        
        winners = random.sample(users, details["winners"])
        winner_mentions = ", ".join(winner.mention for winner in winners)
        await channel.send(f"🎉 Congratulations {winner_mentions}! You won **{details['prize']}**!")
        del self.active_giveaways[message_id]

    @commands.command(name="giveaway_notify")
    async def giveaway_notify(self, ctx, action: str):
        """Subscribes or unsubscribes users from giveaway notifications."""
        if action.lower() == "subscribe":
            if ctx.author.id not in self.notifications:
                self.notifications[ctx.author.id] = []
                await ctx.send(f"You've subscribed to giveaway notifications.")
            else:
                await ctx.send("You're already subscribed.")
        elif action.lower() == "unsubscribe":
            if ctx.author.id in self.notifications:
                del self.notifications[ctx.author.id]
                await ctx.send(f"You've unsubscribed from giveaway notifications.")
            else:
                await ctx.send("You're not subscribed.")
        else:
            await ctx.send("Use 'subscribe' or 'unsubscribe' to manage notifications.")

    @commands.command(name="giveaway_list")
    async def giveaway_list(self, ctx):
        """Lists active giveaways."""
        if not self.active_giveaways:
            await ctx.send("No active giveaways at the moment.")
            return

        giveaways = "\n".join(
            [f"Giveaway {msg_id}: Prize - {details['prize']}, Time Remaining - {details['duration']} seconds"
             for msg_id, details in self.active_giveaways.items()]
        )
        await ctx.send(f"Active Giveaways:\n{giveaways}")

    @commands.command(name="giveaway_cancel")
    async def giveaway_cancel(self, ctx, message_id: int):
        """Cancels a giveaway."""
        if message_id in self.active_giveaways:
            del self.active_giveaways[message_id]
            await ctx.send(f"Giveaway with ID {message_id} has been canceled.")
        else:
            await ctx.send(f"Giveaway with ID {message_id} does not exist.")

async def setup(bot):
    await bot.add_cog(Giveaway(bot))
    