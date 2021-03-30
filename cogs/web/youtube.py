from discord.ext import commands
from discord.utils import escape_markdown
from assets.functions import initembed, Flags
from munch import munchify
import youtubesearchpython.__future__ as yt


class YouTube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["yt"])
    async def youtube(self, ctx, *, args=None):
        if not args:
            await ctx.send_help(self.youtube)
            return

        results = await yt.VideosSearch(args, limit=1).next()
        await ctx.send(f"https://youtu.be/{results['result'][0]['id']}")

    @commands.command(aliases=["ytsearch", "searchyt"])
    async def youtubesearch(self, ctx, *args):
        if not args:
            await ctx.send_help(self.youtubesearch)
            return

        f = Flags(args)
        f.addflag("--count", True, 4)
        args, flags = f.splitflags()

        results = await yt.VideosSearch(" ".join(args), limit=flags["--count"]).next()
        title = escape_markdown(" ".join(args))
        if len(title) > 227:
            title = title[:224] + "..."

        e = initembed(
            ctx=ctx,
            title=f"YouTube search results for `{title}`",
            description="Type a number to select a video",
            image="youtubesearch",
            bordercolour=0xFF0000
        )
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
