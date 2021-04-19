from discord.ext import commands
from assets.functions import initembed, plaintext, Flags
from asyncio import TimeoutError
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
        if results["result"]:
            await ctx.send(f"https://youtu.be/{results['result'][0]['id']}")
        else:
            e = initembed(
                ctx=ctx,
                title=f"No YouTube results found for {plaintext(args, 225)}",
                image="youtubesearch",
                bordercolour=0xFF0000
            )
            await ctx.send(embed=e.embed, file=e.file)

    @commands.command(aliases=["searchyoutube", "ytsearch", "searchyt"])
    async def youtubesearch(self, ctx, *args):
        if not args:
            await ctx.send_help(self.youtubesearch)
            return

        f = Flags(args)
        f.addflag("--count", True, 4)
        args, flags = f.splitflags()

        results = await yt.VideosSearch(" ".join(args), limit=flags["--count"]).next()
        title = plaintext(" ".join(args), 225)

        e = initembed(
            ctx=ctx,
            title=f"YouTube search results for {title}",
            description="Type a number to select a video" if results["result"] else "No results found",
            image="youtubesearch",
            bordercolour=0xFF0000
        )
        for i, result in enumerate(results["result"]):
            result = munchify(result)
            result.viewCount.text = f"`{result.viewCount.short[:-6]}` views" if result.viewCount.short else "Live Video"
            e.embed.add_field(
                name=f"**{i + 1}.** {result.title}",
                value=f"Duration `{result.duration}`, {result.viewCount.text}\n"
                      f"{result.descriptionSnippet[0].text if result.descriptionSnippet else 'No description'}",
                inline=False
            )
        menu = await ctx.send(embed=e.embed, file=e.file)

        def check(message):
            try:
                return True if 0 < int(message.content) <= flags["--count"] else False
            except ValueError:
                return False

        try:
            choice = await self.bot.wait_for("message", check=check, timeout=120)
            choice = int(choice.content)
            await ctx.send(f"https://youtu.be/{results['result'][choice - 1]['id']}")
        except TimeoutError:
            e.embed.description = "Command timed out"
            e.embed.clear_fields()
            await menu.edit(embed=e.embed)


def setup(bot):
    bot.add_cog(YouTube(bot))
