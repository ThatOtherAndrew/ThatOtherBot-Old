from discord.ext import commands
from assets.functions import initembed
from munch import munchify
import youtubesearchpython.__future__ as yt


class YouTube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["yt"])
    async def youtube(self, ctx, *, args):
        results = await yt.VideosSearch(args, limit=1).next()
        await ctx.send(f"https://youtu.be/{results['result'][0]['id']}")

    @commands.command(aliases=["ytsearch", "searchyt"])
    async def youtubesearch(self, ctx, *args):
        results = await yt.VideosSearch(" ".join(args), limit=9).next()
        e = initembed(ctx, "YouTube search results", "Type a number to select a video", "youtubesearch", 0xFF0000)
        for i, result in enumerate(results["result"]):
            result = munchify(result)
            result.viewCount.text = f"`{result.viewCount.text[:-6]}` views" if result.viewCount.text else "Premiere"
            e.embed.add_field(
                name=f"**{i + 1}.** {result.title}",
                value=f"Duration `{result.duration}`, {result.viewCount.text}\n"
                      f"{result.descriptionSnippet[0].text}",
                inline=False
            )
        await ctx.send(embed=e.embed, file=e.file)


def setup(bot):
    bot.add_cog(YouTube(bot))
