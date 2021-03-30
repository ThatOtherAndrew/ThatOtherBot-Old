from discord import User
from discord.ext import commands
from assets.functions import loadjson, Flags
from random import choice


class Kill(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def kill(self, ctx, user: commands.Greedy[User] = None, *args):
        messages = loadjson("cogs.fun.kill")

        if ctx.message.raw_role_mentions:
            await ctx.send(f"*{choice(messages.murder).format(ctx.author.mention, self.bot.user.mention)} "
                           "for trying to ping a role*")
            return

        f = Flags(args)
        f.addflag("--victim", True)
        f.addflag("--killer", True)
        f.addflag("--weapon", True)
        f.addflag("--reason", True)
        args, flags = f.splitflags()
        victim = flags["--victim"] if flags["--victim"] is not None else user[0].mention if user else \
            ctx.message.reference.resolved.author.mention if ctx.message.reference is not None else ctx.author.mention
        killer = flags["--killer"] if flags["--killer"] is not None else \
            "themselves" if victim == ctx.author.mention else ctx.author.mention
        weapon = flags["--weapon"] if flags["--weapon"] is not None else choice(messages.helditems)
        reason = flags["--reason"] if flags["--reason"] is not None else " ".join(args) if args else None

        if flags["--weapon"] or args:
            deathmessage = choice(messages.weapon).format(victim, killer, weapon)
        elif flags["--victim"] or user or ctx.message.reference:
            deathmessage = choice((
                choice(messages.murder).format(victim, killer),
                choice(messages.weapon).format(victim, killer, weapon)
            ))
        else:
            deathmessage = choice((
                choice(messages.death).format(victim),
                choice(messages.murder).format(victim, killer),
                choice(messages.weapon).format(victim, killer, weapon)
            ))

        await ctx.send(f"*{deathmessage.rstrip() + (f' for {reason}' if reason else '')}*")


def setup(bot):
    bot.add_cog(Kill(bot))
