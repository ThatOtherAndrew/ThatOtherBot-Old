#!/usr/bin/env python3.9
import aiohttp
from discord.ext import commands
from assets.functions import *

import re


# Changes execution directory to the script location
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Create bot instance
intents = discord.Intents.default()
intents.members = True

allowedmentions = discord.AllowedMentions.all()
allowedmentions.everyone = False
allowedmentions.roles = False


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aiohttpsession = None

    async def login(self, *args, **kwargs):
        print(f"{colour.Fore.YELLOW}[+] Initialising session")

        print(f"{colour.Fore.YELLOW} │  {colour.Fore.RESET}[-] Create aiohttp client session", end="")
        self.aiohttpsession = aiohttp.ClientSession()
        print(f"\r{colour.Fore.YELLOW} │  {colour.Fore.GREEN}[O] Create aiohttp client session")

        print(f"{colour.Fore.YELLOW} │  {colour.Fore.RESET}[-] Connect to Discord", end="")
        try:
            await super().login(*args, **kwargs)
            print(f"\r{colour.Fore.YELLOW} │  {colour.Fore.GREEN}[O] Connect to Discord")

        except Exception as loginerror:
            if str(loginerror).startswith("Cannot connect to host"):
                print(f"\r{colour.Fore.YELLOW} │  {colour.Fore.RED}[X] Couldn't connect to Discord\n"
                      f"{colour.Fore.YELLOW} │  {colour.Fore.RED} │  "
                      f"Is Discord down or inaccessible? Is there an internet connection?")

            elif str(loginerror) == "Improper token has been passed.":
                print(f"\r{colour.Fore.RED}[X] Error: Invalid token. Please check if"
                      " the environment variable \"env.DISCORDTOKEN\" is valid.")

            else:
                print(f"{colour.Fore.RED}[X] Error: Uncaught exception during bot initialisation.")

            print(f"{colour.Fore.YELLOW} │  {colour.Fore.RED} │  Error details:\n"
                  f"{colour.Fore.YELLOW} │  {colour.Fore.RED} │   - {loginerror}")

    async def close(self):
        await super().close()
        if self.aiohttpsession:
            await self.aiohttpsession.close()


bot = Bot(
    command_prefix=config.prefixes,
    case_insensitive=True,
    allowed_mentions=allowedmentions,
    intents=intents,
    status=discord.Status.online,
    activity=[
        discord.Game(name=config.presence.message),
        discord.Activity(type=discord.ActivityType.watching, name=config.presence.message),
        discord.Activity(type=discord.ActivityType.listening, name=config.presence.message),
        discord.Activity(type=discord.ActivityType.competing, name=config.presence.message)
    ][config.presence.type - 1] if config.presence.type in range(1, 5) else discord.Game(name=config.presence.message)
)


@bot.event
async def on_connect():
    print(f"\r{colour.Fore.YELLOW}[+] Getting ready...", end="")


@bot.event
async def on_ready():
    print(f"\r{colour.Fore.GREEN}[O] Logged in as {colour.Fore.YELLOW}{bot.user}{colour.Fore.GREEN}, "
          f"client ID {colour.Fore.YELLOW}{str(bot.user.id)}")
    print(f"{colour.Style.BRIGHT}{'═' * (len(str(bot.user)) + len(str(bot.user.id)) + 29)}")


# Core event-based operations
@bot.event
async def on_message(message):
    # Ignore self
    if message.author == bot.user:
        return

    # Debug mode
    if config.debug:
        print(f"[-] DEBUG: {message.content}")

    if re.search(f"<@!?{bot.user.id}>", message.content):
        if re.fullmatch(f"<@!?{bot.user.id}>", message.content):
            prefix = plaintext(config.prefixes[0])
            await message.channel.send(f"Hey, that's me! (My prefix is {prefix}, in case you forgot, you numpty.)")
        else:
            await message.channel.send("Hey, that's me!")

    # Process command-based operations
    await bot.process_commands(message)


# Core command-based operations

# General use commands
@bot.command()
async def test(ctx):
    """A test message to check if the bot is responding"""
    await ctx.send(":thumbsup: Received!")


# Bot admin commands
@bot.command(aliases=["echo"])
async def say(ctx, *, args=None):
    """Sends a message"""
    if args is None:
        await ctx.send_help(say)
        return

    if ctx.author.id in config.staff.admins:
        await ctx.message.delete()
        await ctx.send(args)
    else:
        await ctx.send(
            f":octagonal_sign: **You can't use that!** {ctx.author.mention}, you have to be a bot admin to use the "
            f"{plaintext(config.prefixes[0] + ctx.invoked_with)} command.")


@bot.command(aliases=["exec"])
async def execute(ctx, *, args=None):
    """Executes a line of Python code"""
    if args is None:
        await ctx.send_help(execute)
        return

    if ctx.author.id in config.staff.admins:
        try:
            exec(args)
            await ctx.message.add_reaction("👍")
        except Exception as exception:
            await reporterror(ctx, exception)
    else:
        await ctx.send(
            f":octagonal_sign: **You can't use that!** {ctx.author.mention}, you have to be a bot admin to use the "
            f"{plaintext(config.prefixes[0] + ctx.invoked_with)} command.")


@bot.command(aliases=["eval"])
async def evaluate(ctx, *, args=None):
    """Evaluates a Python expression in the current scope and returns the result"""
    if args is None:
        await ctx.send_help(evaluate)
        return

    if ctx.author.id in config.staff.admins:
        try:
            await ctx.send(eval(args))
        except Exception as exception:
            await reporterror(ctx, exception)
    else:
        await ctx.send(
            f":octagonal_sign: **You can't use that!** {ctx.author.mention}, you have to be a bot admin to use the "
            f"{plaintext(config.prefixes[0] + ctx.invoked_with)} command.")


@bot.command()
async def disable(ctx, command):
    """Disables a command to prevent it from being used"""
    if ctx.author.id in config.staff.admins:
        if bot.get_command(command).enabled:
            bot.get_command(command).enabled = False
            await ctx.send(f":ok_hand: The {command} command is now disabled, and cannot be used until you use "
                           f"{plaintext(config.prefixes[0] + 'enable ' + command)}.")
        else:
            await ctx.send(f"The {command} command is already disabled!")


@bot.command()
async def enable(ctx, command):
    """Enables a previously disabled command"""
    if ctx.author.id in config.staff.admins:
        if not bot.get_command(command).enabled:
            bot.get_command(command).enabled = True
            await ctx.send(f":ok_hand: The {command} command is now enabled, and can be used.")
        else:
            await ctx.send(f"The {command} command is already enabled!")


@bot.command()
async def reload(ctx, *args):
    """Reloads the specified extensions, or everything if no extensions specified"""
    if ctx.author.id in config.staff.admins:
        print(f"{colour.Fore.YELLOW}[+] Reloading extensions")
        reloadedextensions = []
        successfulreloads = []
        failedreloads = []
        args = [""] if args == () else args

        for reloadpath in args:
            for extensionpath in getextensions(reloadpath):
                if extensionpath not in reloadedextensions:
                    reloadedextensions.append(extensionpath)
                    if extensionpath is None:
                        print(f"{colour.Fore.YELLOW} │  {colour.Fore.RED}[X] "
                              f"No extensions found in path cogs.{reloadpath}")
                        failedreloads.append(f"- Invalid path: {reloadpath}")
                        continue
                    print(f"{colour.Fore.YELLOW} │  {colour.Fore.RESET}[-] " + extensionpath, end="")
                    try:
                        bot.reload_extension(extensionpath)
                        print(f"\r{colour.Fore.YELLOW} │  {colour.Fore.GREEN}[O] {extensionpath}")
                        successfulreloads.append(f"+ {extensionpath}")
                    except Exception as exception:
                        print(f"\r{colour.Fore.YELLOW} │  {colour.Fore.RED}[X] {extensionpath}\n"
                              f"{colour.Fore.YELLOW} │  {colour.Fore.RED}  - {exception}")
                        failedreloads.append(f"- Unknown error: {exception}")

        e = initembed(ctx, f"Reloaded {len(reloadedextensions)} extension{'s' if len(reloadedextensions) != 1 else ''}")
        e.add_field(
            name="Successful reloads",
            value="```diff\n" + "\n".join(successfulreloads) + "```",
            inline=False
        ) if successfulreloads else None
        e.add_field(
            name="Failed reloads",
            value="```diff\n" + "\n".join(failedreloads) + "```",
            inline=False
        ) if failedreloads else None
        await ctx.send(embed=e)
    else:
        await ctx.send(
            f":octagonal_sign: **You can't use that!** {ctx.author.mention}, you have to be a bot admin to use the "
            f"{plaintext(config.prefixes[0] + ctx.invoked_with)} command.")


# Command logging in console
@bot.event
async def on_command_completion(ctx):
    print(f"[-] {ctx.author} ({ctx.author.id}) ran the command {colour.Style.BRIGHT}{ctx.message.content}")


# Error catching
@bot.event
async def on_command_error(ctx, exception):
    """Catches exceptions raised during usage of the bot"""
    ignoredexceptions = [commands.errors.CommandNotFound, commands.errors.DisabledCommand]
    if exception not in ignoredexceptions:
        await reporterror(ctx, exception)


# Load all extensions in the cogs directory
print(f"{colour.Fore.YELLOW}[+] Loading extensions")

try:
    for extension in getextensions():
        print(f"\r{colour.Fore.YELLOW} │  {colour.Fore.RESET}[-] {extension}", end="")
        try:
            bot.load_extension(extension)
            print(f"\r{colour.Fore.YELLOW} │  {colour.Fore.GREEN}[O] {extension}")
        except Exception as extensionerror:
            print(f"\r{colour.Fore.YELLOW} │  {colour.Fore.RED}[X] {extension}\n"
                  f"{colour.Fore.YELLOW} │  {colour.Fore.RED}  - {extensionerror}")
except TypeError:
    print(f"{colour.Fore.RED}[!] No extensions loaded. This is likely due to a missing cogs directory!")


# Run the bot!
if __name__ == "__main__":
    bot.run(env.DISCORDTOKEN)

print(f"{colour.Fore.RED}{colour.Style.BRIGHT}[Session ended]")
