import aiohttp
from discord.ext import commands
from assets.functions import env, initembed
from munch import munchify
from urllib.parse import quote_plus


class WolframAlpha(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.conversations = {}

    @commands.command(aliases=["wa", "wolfram", "alpha", "grumbot"])
    async def wolframalpha(self, ctx, *, args=None):
        if not args:
            await ctx.send_help(self.wolframalpha)
            return

        async with ctx.channel.typing():
            url = "https://api.wolframalpha.com/v1/conversation.jsp?" \
                f"appid={env.WOLFRAMTOKEN}" \
                f"&i={quote_plus(args)}"
            url += f"&conversationid={self.conversations[ctx.author.id]}" if ctx.author.id in self.conversations else ""

            async with aiohttp.request("GET", url) as resp:
                response = munchify(await resp.json())

            if not hasattr(response, "error"):
                self.conversations[ctx.author.id] = response.conversationID
                e = initembed(ctx, "Wolfram|Alpha", bordercolour=0xFF6600)
                e.add_field(name="Response", value=response.result)
            else:
                e = initembed(ctx, "Wolfram|Alpha", bordercolour=0xFF0000)
                e.add_field(name="Error", value=response.error)

            await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(WolframAlpha(bot))
