from discord.ext import commands
from assets.functions import env, initembed
from munch import Munch, munchify
from urllib.parse import quote_plus


class WolframAlpha(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.conversations = Munch()

    @commands.command(aliases=["wa", "wolfram", "alpha", "grumbot"])
    async def wolframalpha(self, ctx, *, args=None):
        if not args:
            await ctx.send_help(self.wolframalpha)
            return

        async with ctx.channel.typing():
            if ctx.author.id not in self.conversations:
                self.conversations[ctx.author.id] = munchify({"host": "", "id": "", "s": ""})

            url = f"https://{self.conversations[ctx.author.id].host or 'api.wolframalpha.com'}/v1/conversation.jsp?" \
                f"appid={env.WOLFRAMTOKEN}" \
                f"&i={quote_plus(args)}"
            if self.conversations[ctx.author.id].id:
                url += f"&conversationid={self.conversations[ctx.author.id].id}"
            if self.conversations[ctx.author.id].s:
                url += f"&s={self.conversations[ctx.author.id].s}"

            async with self.bot.aiohttpsession.request("GET", url) as resp:
                response = munchify(await resp.json(content_type="application/json"))

            if not hasattr(response, "error"):
                self.conversations[ctx.author.id].host = response.host + "/api"
                self.conversations[ctx.author.id].id = response.conversationID
                self.conversations[ctx.author.id].s = response.s if hasattr(response, "s") else ""
                e = initembed(ctx, "Wolfram|Alpha", bordercolour=0xFF6600)
                e.add_field(name="Response", value=response.result)
            else:
                e = initembed(ctx, "Wolfram|Alpha", bordercolour=0xFF0000)
                e.add_field(name="Error", value=response.error)

            await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(WolframAlpha(bot))
