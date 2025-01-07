from discord.ext import commands
import discord

class Donations(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='donation')
    async def donation(self, ctx):
        """Displays information about the studio and ways to support it."""
        embed = discord.Embed(
            title="🎨 Support Twisted Fairytale Studio 🌟",
            description=(
                "Twisted Fairytale Studio is dedicated to creating unique, feature-rich Discord bots like **Red Riding Hood**. "
                "If you'd like to support our work, here are a few magical ways to do so:\n\n"
                "💖 **Patreon**: [Support us on Patreon](///)\n"
                "🚀 **Kickstarter**: [Back our projects on Kickstarter](///)\n"
                "💸 **PayPal**: [Donate via PayPal](///)\n\n"
                "✨ Your contributions help us continue weaving stories into our bots. Thank you! ✨"
            ),
            color=0xFF69B4  # A vibrant pink for creativity
        )
        embed.set_footer(text="🧙‍♀️ Twisted Fairytale Studio | Thank you for your support! 🪄")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Donations(bot))
  