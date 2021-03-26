from discord.ext import commands
from assets.functions import *

import re

# Changes execution directory to the script location
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Create bot instance
bot = commands.Bot(
    command_prefix=config.prefixes,
    case_insensitive=True,
    status=discord.Status.online,
    activity=[
        discord.Game(name=config.presence.message),
        discord.Activity(type=discord.ActivityType.watching, name=config.presence.message),
        discord.Activity(type=discord.ActivityType.listening, name=config.presence.message),
        discord.Activity(type=discord.ActivityType.competing, name=config.presence.message)
    ][config.presence.type - 1] if config.presence.type in range(1, 5) else discord.Game(name=config.presence.message)
)


# Initialising the bot
@bot.event
async def on_ready():
    print(f"{colour.Fore.GREEN}[O] Logged in as {colour.Fore.YELLOW}{bot.user}{colour.Fore.GREEN}, client ID "
          f"{colour.Fore.YELLOW}{str(bot.user.id)}\n{colour.Fore.RESET}{colour.Style.BRIGHT}{'═' * 32}")


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
        await message.channel.send(
            "Hey, that's me!" + (f" (My prefix is `{config.prefixes[0]}`, in case you forgot, you numpty.)"
                                 if re.fullmatch(f"<@!?{bot.user.id}>", message.content) else "")
        )

    # Process command-based operations
    await bot.process_commands(message)


# Core command-based operations

# General use commands
@bot.command()
async def test(ctx):
    """A test message to check if the bot is responding"""
    await ctx.send(":thumbsup: Received!")


# Bot admin commands
@bot.command(aliases=["exec"])
async def execute(ctx, *, arg=None):
    """Executes a line of Python code"""
    if ctx.author.id in config.staff.admins:
        try:
            exec(arg)
            await ctx.message.add_reaction("👍")
        except Exception as exception:
            await reporterror(ctx, exception)
    else:
        await ctx.send(
            f":octagonal_sign: **You can't use that!** {ctx.author.mention}, you have to be a bot admin to use the "
            f"`{config.prefixes[0] + ctx.invoked_with}` command.")


@bot.command(aliases=["eval"])
async def evaluate(ctx, *, arg=None):
    """Evaluates a Python expression in the current scope and returns the result"""
    if ctx.author.id in config.staff.admins:
        try:
            await ctx.send(f"```{eval(arg)}```")
        except Exception as exception:
            await reporterror(ctx, exception)
    else:
        await ctx.send(
            f":octagonal_sign: **You can't use that!** {ctx.author.mention}, you have to be a bot admin to use the "
            f"`{config.prefixes[0] + ctx.invoked_with}` command.")


@bot.command()
async def disable(ctx, command):
    """Disables a command to prevent it from being used"""
    if ctx.author.id in config.staff.admins:
        if bot.get_command(command).enabled:
            bot.get_command(command).enabled = False
            await ctx.send(f":ok_hand: The {command} command is now disabled, and cannot be used until you use "
                           f"`{config.prefixes[0]}enable {command}`.")
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
                    print(f"\r{colour.Fore.YELLOW} │  {colour.Fore.RESET}[-] " + extension, end="", flush=True)
                    try:
                        bot.reload_extension(extensionpath)
                        print(f"\r{colour.Fore.YELLOW} │  {colour.Fore.GREEN}[O] {extension}")
                        successfulreloads.append(f"+ {extensionpath}")
                    except Exception as exception:
                        print(f"\r{colour.Fore.YELLOW} │  {colour.Fore.RED}[X] {extension}\n"
                              f"{colour.Fore.YELLOW} │    {colour.Fore.RED}- {exception}")
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
            f"`{config.prefixes[0] + ctx.invoked_with}` command.")


# Command logging in console
@bot.event
async def on_command_completion(ctx):
    print(f"[-] {ctx.author} ({ctx.author.id}) ran the command {colour.Style.BRIGHT}{ctx.message.content}")


# Error catching
@bot.event
async def on_command_error(ctx, exception):
    """Catches exceptions raised during usage of the bot"""
    if exception == commands.errors.CommandNotFound:  # Ignore invalid commands
        pass
    elif exception == commands.errors.DisabledCommand:  # Ignore disabled command call attempts
        pass
    else:
        await reporterror(ctx, exception)


# Load all extensions in the cogs directory
print(f"{colour.Fore.YELLOW}[+] Loading extensions")

try:
    for extension in getextensions():
        print("\r │  [-] " + extension, end="", flush=True)
        try:
            bot.load_extension(extension)
            print(f"\r{colour.Fore.YELLOW} │  {colour.Fore.GREEN}[O] {extension}")
        except Exception as error:
            print(f"\r{colour.Fore.YELLOW} │  {colour.Fore.RED}[X] {extension}\n"
                  f"{colour.Fore.YELLOW} │    {colour.Fore.RED}- {error}")
except TypeError:
    print(f"{colour.Fore.RED}[!] No extensions loaded. This is likely due to a missing cogs directory!")


# Run the bot!
print(f"{colour.Fore.YELLOW}[+] Initialising session")

if __name__ == "__main__":
    try:
        bot.run(env.DISCORDTOKEN)
    except Exception as error:
        if str(error).startswith("Cannot connect to host"):
            print(f"{colour.Fore.RED}[X] Error: Network connection failed. "
                  "Is Discord down or inaccessible? Is there an internet connection?")

        elif str(error) == "Improper token has been passed.":
            print(f"{colour.Fore.RED}[X] Error: Invalid token. Please check if"
                  " the environment variable \"env.DISCORDTOKEN\" is valid.")

        else:
            print(f"{colour.Fore.RED}[X] Error: Uncaught exception during bot initialisation.")

        print(f"{colour.Fore.RED} |  Error details: {error}")

print(f"{colour.Fore.RED}{colour.Style.BRIGHT}[Session ended]")
