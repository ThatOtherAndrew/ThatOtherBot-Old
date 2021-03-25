from discord.ext import commands
from assets.functions import *


class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        e = initembed(ctx, ":ping_pong: Pong!")
        e.add_field(name="Latency", value=f"`{round(self.bot.latency * 1000)}ms`")
        await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(Ping(bot))
