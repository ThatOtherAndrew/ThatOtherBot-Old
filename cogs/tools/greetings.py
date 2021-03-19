from assets.functions import *
from discord.ext import commands


class Join(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, ctx):
        print("Test")
        e = initembed(ctx, "Welcome!", "Someone new has joined the server!")
        await ctx.send(embed=e)


class Leave(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_leave(self, ctx):
        print("Test")
        e = initembed(ctx, "Goodbye!", "Someone new has joined the server!")
        await ctx.send(embed=e)
