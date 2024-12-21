import discord
from discord.ext import commands
import random
import re
from datetime import datetime, timedelta
from discord.utils import sleep_until
from db import connect_to_db

class Social(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_connection = connect_to_db()

    @commands.command()
    async def setchannel(self, ctx, channel: discord.TextChannel):
        """Set the default giveaway channel."""
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send("You don't have permission to set the giveaway channel.")
            return

        cursor = self.db_connection.cursor()
        query = """
        INSERT INTO server_configs (guild_id, config_key, config_value)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE config_value = %s;
        """
        guild_id = ctx.guild.id
        config_key = "giveaway_channel"
        config_value = str(channel.id)

        cursor.execute(query, (guild_id, config_key, config_value, config_value))
        self.db_connection.commit()
        cursor.close()

        await ctx.send(f"Giveaway channel has been set to {channel.mention}.")

    @commands.command()
    async def giveaway(self, ctx, prize: str, duration: str):
        """Start a giveaway with a specified prize and duration."""
        # Retrieve giveaway channel from the database
        cursor = self.db_connection.cursor(dictionary=True)
        query = "SELECT config_value FROM server_configs WHERE guild_id = %s AND config_key = %s;"
        cursor.execute(query, (ctx.guild.id, "giveaway_channel"))
        result = cursor.fetchone()
        cursor.close()

        if not result:
            await ctx.send("No giveaway channel has been set. Use `r.setchannel #channel` first.")
            return

        giveaway_channel_id = int(result['config_value'])
        giveaway_channel = self.bot.get_channel(giveaway_channel_id)
        if not giveaway_channel:
            await ctx.send("The giveaway channel is no longer accessible. Please set a valid channel.")
            return

        # Parse duration
        duration_seconds = self.parse_duration(duration)
        if duration_seconds is None:
            await ctx.send("Invalid time format. Use format like `1d 2h 30m`.")
            return

        # Post the giveaway message
        giveaway_msg = await giveaway_channel.send(
            f"🎉 **GIVEAWAY TIME** 🎉\nPrize: {prize}\nReact with 🎉 to enter!\nTime remaining: {duration}!"
        )
        await giveaway_msg.add_reaction("🎉")

        # Save giveaway data to the database
        query = """
        INSERT INTO giveaways (message_id, channel_id, guild_id, prize, end_time)
        VALUES (%s, %s, %s, %s, %s);
        """
        end_time = datetime.utcnow() + timedelta(seconds=duration_seconds)
        cursor = self.db_connection.cursor()
        cursor.execute(query, (giveaway_msg.id, giveaway_channel.id, ctx.guild.id, prize, end_time))
        self.db_connection.commit()
        cursor.close()

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

                # Delete giveaway record from the database
                cursor = self.db_connection.cursor()
                query = "DELETE FROM giveaways WHERE message_id = %s;"
                cursor.execute(query, (message.id,))
                self.db_connection.commit()
                cursor.close()
            else:
                await message.channel.send("No participants, giveaway has been canceled.")
        else:
            await message.channel.send("No reactions received, giveaway canceled.")

    @commands.command()
    async def endgiveaway(self, ctx, message_id: int):
        """Forcefully end a giveaway and pick a winner."""
        cursor = self.db_connection.cursor(dictionary=True)
        query = "SELECT * FROM giveaways WHERE message_id = %s AND guild_id = %s;"
        cursor.execute(query, (message_id, ctx.guild.id))
        giveaway = cursor.fetchone()
        cursor.close()

        if not giveaway:
            await ctx.send("Giveaway not found.")
            return

        channel = self.bot.get_channel(int(giveaway["channel_id"]))
        if not channel:
            await ctx.send("The channel for this giveaway is no longer accessible.")
            return

        try:
            giveaway_message = await channel.fetch_message(message_id)
        except discord.NotFound:
            await ctx.send("Giveaway message not found.")
            return

        # Simulate waiting for the end of the giveaway
        await self.wait_for_giveaway_end(giveaway_message, 0, giveaway["prize"])

async def setup(bot):
    await bot.add_cog(Social(bot))
