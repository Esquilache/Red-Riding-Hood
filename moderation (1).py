import discord
from discord.ext import commands
from typing import Optional
import mysql.connector
import os
from dotenv import load_dotenv
import asyncio
import db

load_dotenv()  # Load environment variables from .env

    # Log infractions to the database
def log_infraction(self, user_id, guild_id, moderator_id, infraction_type, reason):
        self.cursor.execute("""
        INSERT INTO infractions (user_id, guild_id, moderator_id, infraction_type, reason)
        VALUES (%s, %s, %s, %s, %s)
        """, (user_id, guild_id, moderator_id, infraction_type, reason))
        self.db.commit()

    # Ban Command
    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: Optional[str] = "No reason provided."):
        """Bans a member and logs the infraction."""
        await member.ban(reason=reason, delete_message_days=7)
        self.log_infraction(member.id, ctx.guild.id, ctx.author.id, "Ban", reason)
        await ctx.send(f"🔨 {member.mention} has been banned. Reason: {reason}")

    # Unban Command
    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        user = await self.bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(f"✅ {user.mention} has been unbanned.")

    # Kick Command
  @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: Optional[str] = "No reason provided."):
        """Kicks a member and logs the infraction."""
        await member.kick(reason=reason)
        self.log_infraction(member.id, ctx.guild.id, ctx.author.id, "Kick", reason)
        await ctx.send(f"👢 {member.mention} has been kicked. Reason: {reason}")

    # Mute Command
  @commands.command(name="mute")
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, duration: Optional[int] = None, *, reason: Optional[str] = "No reason provided."):
        """Mutes a member for an optional duration and logs the infraction."""
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not mute_role:
            mute_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(mute_role, send_messages=False)
        await member.add_roles(mute_role, reason=reason)
        self.log_infraction(member.id, ctx.guild.id, ctx.author.id, "Mute", reason)
        if duration:
            await ctx.send(f"🔇 {member.mention} has been muted for {duration} minutes. Reason: {reason}")
            await asyncio.sleep(duration * 60)
            await member.remove_roles(mute_role)
            await ctx.send(f"🔊 {member.mention} is now unmuted.")
        else:
            await ctx.send(f"🔇 {member.mention} has been muted indefinitely. Reason: {reason}")

    # Warn Command
  @commands.command(name="warn")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str):
        """Issues a warning to a user and logs the infraction."""
        self.log_infraction(member.id, ctx.guild.id, ctx.author.id, "Warn", reason)
        await ctx.send(f"⚠️ {member.mention} has been warned. Reason: {reason}")

    # Purge Command
  @commands.command(name="purge")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: Optional[int] = 10):
        """Deletes the specified number of messages."""
        if amount == "all":
            await ctx.send("⚠️ Purging all messages is not allowed. Specify a number instead.")
        else:
            await ctx.channel.purge(limit=amount)
            await ctx.send(f"🧹 Cleared {amount} messages.", delete_after=5)
    
    # Infractions Command
  @commands.command(name="infractions")
    @commands.has_permissions(manage_messages=True)
    async def infractions(self, ctx, member: discord.Member):
        self.cursor.execute("SELECT infraction_type, reason, timestamp FROM infractions WHERE user_id = %s AND guild_id = %s",
                            (member.id, ctx.guild.id))
        rows = self.cursor.fetchall()
        if rows:
            embed = discord.Embed(title=f"Infractions for {member}", color=discord.Color.orange())
            for infraction_type, reason, timestamp in rows:
                embed.add_field(name=f"{infraction_type} - {timestamp.strftime('%Y-%m-%d %H:%M:%S')}", value=reason, inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"ℹ️ No infractions found for {member.mention}.")

    # Additional Commands: Slowmode, Nickname, etc.
  @commands.command(name="slowmode")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int):
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.send(f"🐢 Slowmode set to {seconds} seconds.")

    @commands.command(name="nickname")
    @commands.has_permissions(manage_nicknames=True)
    async def nickname(self, ctx, member: discord.Member, *, nickname: Optional[str] = None):
        await member.edit(nick=nickname)
        await ctx.send(f"📝 Changed nickname for {member.mention} to {nickname if nickname else 'default'}.")
      
    
    # Modlog Command
  @commands.command(name="modlog")
    @commands.has_permissions(manage_messages=True)
    async def modlog(self, ctx, member: discord.Member):
        self.cursor.execute("SELECT * FROM infractions WHERE user_id = %s AND guild_id = %s",
                            (member.id, ctx.guild.id))
        rows = self.cursor.fetchall()
        if rows:
            embed = discord.Embed(title=f"Moderation Log for {member}", color=discord.Color.purple())
            for infraction_id, user_id, guild_id, moderator_id, infraction_type, reason, timestamp in rows:
                moderator = await self.bot.fetch_user(moderator_id)
                embed.add_field(
                    name=f"Case {infraction_id} - {infraction_type}",
                    value=f"Reason: {reason}\nModerator: {moderator}\nDate: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
                    inline=False
                )
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"ℹ️ No moderation history found for {member.mention}.")

   # Lock Channel
  @commands.command(name="lock")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        """Locks the current channel."""
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send("🔒 Channel locked.")

    # Unlock Channel
  @commands.command(name="unlock")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        """Unlocks the current channel."""
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send("🔓 Channel unlocked.")
  
# Setup function to add the cog
async def setup(bot):
    await bot.add_cog(ModerationCog(bot))
    
