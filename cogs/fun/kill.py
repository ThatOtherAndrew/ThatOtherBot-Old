from discord import Member
from discord.ext import commands
from assets.functions import loadjson, Flags
from random import choice
from typing import Optional


class Kill(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def kill(self, ctx, user: Optional[Member] = None, *, args: str = ""):
        f = Flags(args.split())
        f.addflag("--victim", True)
        f.addflag("--killer", True)
        f.addflag("--weapon", True)
        f.addflag("--reason", True)
        args, flags = f.splitflags()

        for key in ("--victim", "--killer"):
            try:
                flags[key] = (await commands.MemberConverter().convert(ctx, flags[key] or "")).mention
            except commands.errors.MemberNotFound:
                pass

        # DEBUG
        await ctx.send(f"!!DEBUG!!\n{user=}\n{args=}")

        messages = loadjson("cogs.fun.kill")

        # Safeguard to prevent pinging roles
        if ctx.message.raw_role_mentions:
            await ctx.send(f"*{choice(messages.murder).format(ctx.author.mention, self.bot.user.mention)} "
                           "for trying to ping a role*")
            return

        if flags["--weapon"] is None:
            if not (user or flags["--killer"]):
                deathmessage = choice(messages.death).format(
                    flags["--victim"] or ctx.author.mention
                )
            else:
                deathmessage = choice(messages.murder).format(
                    victim := flags["--victim"] or (user.mention if user else None) or ctx.author.mention,
                    flags["--killer"] or ("themselves" if victim == ctx.author.mention else ctx.author.mention)
                )
        else:
            deathmessage = choice(messages.weapon).format(
                victim := flags["--victim"] or (user.mention if user else None) or ctx.author.mention,
                flags["--killer"] or ("themselves" if victim == ctx.author.mention else user.mention),
                choice(messages.helditems) if flags["--weapon"].lower() == "random" else flags["--weapon"]
            )

        if flags['--reason'] or args:
            deathmessage += f" for {(flags['--reason'] or ' '.join(args)).lstrip('for').strip()}"

        await ctx.send(f"*{deathmessage}*")


def setup(bot):
    bot.add_cog(Kill(bot))
