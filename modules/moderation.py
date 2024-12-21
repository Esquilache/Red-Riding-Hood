import discord
from discord.ext import commands
import json
import asyncio
from datetime import datetime

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warning_file = "warnings.json"
        # Load warnings file
        try:
            with open(self.warning_file, "r") as f:
                self.warnings = json.load(f)
        except FileNotFoundError:
            self.warnings = {}

    def save_warnings(self):
        """Save warnings to the JSON file."""
        with open(self.warning_file, "w") as f:
            json.dump(self.warnings, f, indent=4)

    # Warning System
    @commands.command()
    async def warn(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        """Warn a user."""
        user_id = str(member.id)
        if user_id not in self.warnings:
            self.warnings[user_id] = []

        # Add warning
        self.warnings[user_id].append({"reason": reason, "date": str(datetime.utcnow())})
        self.save_warnings()

        await ctx.send(f"⚠️ {member.mention} has been warned. Reason: {reason}")

    @commands.command()
    async def warnings(self, ctx, member: discord.Member):
        """List all warnings for a user."""
        user_id = str(member.id)
        if user_id not in self.warnings or len(self.warnings[user_id]) == 0:
            await ctx.send(f"✅ {member.mention} has no warnings.")
            return

        warning_list = self.warnings[user_id]
        warning_messages = [
            f"**{i+1}.** Reason: {warn['reason']} | Date: {warn['date']}"
            for i, warn in enumerate(warning_list)
        ]
        await ctx.send(f"⚠️ {member.mention} Warnings:\n" + "\n".join(warning_messages))

    @commands.command()
    async def clearwarnings(self, ctx, member: discord.Member):
        """Clear all warnings for a user."""
        user_id = str(member.id)
        if user_id not in self.warnings or len(self.warnings[user_id]) == 0:
            await ctx.send(f"✅ {member.mention} has no warnings to clear.")
            return

        self.warnings[user_id] = []
        self.save_warnings()
        await ctx.send(f"✅ Cleared all warnings for {member.mention}.")

    # Temporary Actions
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def tempban(self, ctx, member: discord.Member, duration: int, *, reason: str = "No reason provided"):
        """Temporarily ban a user for a specific duration in seconds."""
        await member.ban(reason=reason)
        await ctx.send(f"⛔ {member.mention} has been banned for {duration} seconds. Reason: {reason}")

        # Unban after duration
        await asyncio.sleep(duration)
        await ctx.guild.unban(member)
        await ctx.send(f"✅ {member.mention} has been unbanned after {duration} seconds.")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def tempmute(self, ctx, member: discord.Member, duration: int, *, reason: str = "No reason provided"):
        """Temporarily mute a user for a specific duration in seconds."""
        # Create a "Muted" role if it doesn't exist
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            muted_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, send_messages=False, speak=False)

        # Add the role
        await member.add_roles(muted_role, reason=reason)
        await ctx.send(f"🔇 {member.mention} has been muted for {duration} seconds. Reason: {reason}")

        # Remove the role after duration
        await asyncio.sleep(duration)
        await member.remove_roles(muted_role)
        await ctx.send(f"✅ {member.mention} is now unmuted after {duration} seconds.")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
