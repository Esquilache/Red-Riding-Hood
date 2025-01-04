import discord
from discord.ext import commands
from typing import Optional
import mysql.connector
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()  # Load environment variables from .env

class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        self.cursor = self.db.cursor()

    # Initialize Database Tables
    @commands.Cog.listener()
    async def on_ready(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS infractions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id BIGINT NOT NULL,
            guild_id BIGINT NOT NULL,
            moderator_id BIGINT NOT NULL,
            infraction_type VARCHAR(50),
            reason TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        self.db.commit()

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

# Setup function to add the cog
async def setup(bot):
    await bot.add_cog(ModerationCog(bot))
    
