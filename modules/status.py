import discord
from discord.ext import commands, tasks
import datetime
import psutil  # Optional: For system stats
import platform

class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.datetime.utcnow()
        self.commands_processed = 0
        self.status_channel_id = 1318451594588848128  # Replace with your #bot-status channel ID
        self.update_bot_status.start()  # Start the loop

    # Helper: Calculate bot uptime
    def get_uptime(self):
        now = datetime.datetime.utcnow()
        uptime_duration = now - self.start_time
        hours, remainder = divmod(int(uptime_duration.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}h {minutes}m {seconds}s"

    # Helper: Update bot status embed
    async def update_status_embed(self):
        channel = self.bot.get_channel(self.status_channel_id)
        if not channel:
            return

        embed = discord.Embed(
            title="🤖 Bot Status",
            color=discord.Color.green(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.add_field(name="🟢 Status", value="Online", inline=False)
        embed.add_field(name="🕒 Uptime", value=self.get_uptime(), inline=True)
        embed.add_field(name="⏱️ Latency", value=f"{round(self.bot.latency * 1000)} ms", inline=True)
        embed.add_field(name="💻 Commands Processed", value=f"{self.commands_processed} commands", inline=True)

        # Optional: Add system stats (requires psutil)
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        embed.add_field(name="📊 CPU Usage", value=f"{cpu_usage}%", inline=True)
        embed.add_field(name="📈 Memory Usage", value=f"{memory_usage}%", inline=True)

        embed.set_footer(text=f"Powered by {platform.system()} | Red Riding Hood by Juarez Software")

        # Send or edit the embed
        if hasattr(self, "status_message"):
            await self.status_message.edit(embed=embed)
        else:
            self.status_message = await channel.send(embed=embed)

    # Task: Periodic updates
    @tasks.loop(minutes=15)
    async def update_bot_status(self):
        await self.update_status_embed()

    # Track commands processed
    @commands.Cog.listener()
    async def on_command(self, ctx):
        self.commands_processed += 1

    # Start the loop when the bot is ready
    @commands.Cog.listener()
    async def on_ready(self):
        print("Status module is active.")

async def setup(bot):
    await bot.add_cog(Status(bot))
