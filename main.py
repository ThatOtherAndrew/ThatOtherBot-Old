from discord.ext import commands

from assets.functions import *

print("Parsing code...")

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
    print(f"Logged in as {bot.user.name}, client ID {str(bot.user.id)}\n================================")


# Core event-based operations
@bot.event
async def on_message(message):
    # Ignore self
    if message.author == bot.user:
        return

    # Debug mode
    if config.debug:
        print(message.content)

    if bot.user in message.mentions:
        await message.channel.send(
            "Hey, that's me!" + (f" (My prefix is `{config.prefixes[0]}`, in case you forgot, you numpty.)"
                                 if re.search(f"^<@!?{bot.user.id}>$", message.content) else "")
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
    """Executes some Python code in the current scope"""
    if ctx.author.id in config.staff.admins:
        try:
            exec(arg)
            await ctx.message.add_reaction("👍")
        except Exception as exception:
            e = initembed(ctx, "An error occurred during execution", image="error")
            e.embed.add_field(name="Exception:", value=str(exception))
            await ctx.send(embed=e.embed, file=e.file)
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
            e = initembed(ctx, "An error occurred during execution", image="error")
            e.embed.add_field(name="Exception:", value=str(exception))
            await ctx.send(embed=e.embed, file=e.file)
    else:
        await ctx.send(
            f":octagonal_sign: **You can't use that!** {ctx.author.mention}, you have to be a bot admin to use the "
            f"`{config.prefixes[0] + ctx.invoked_with}` command.")


@bot.command()
async def disable(ctx, command):
    """Disables a command to prevent it from being used"""
    if ctx.author.id in config.staff.admins:
        if not bot.get_command(command).enabled:
            bot.get_command(command).enabled = True
            await ctx.send(f":ok_hand: The {command} command is now disabled, and cannot be used until you use "
                           f"`{config.prefixes[0]}enable {command}`.")
        else:
            await ctx.send(f"The {command} command is already disabled!")


@bot.command()
async def enable(ctx, command):
    """Enables a previously disabled command"""
    if ctx.author.id in config.staff.admins:
        if bot.get_command(command).enabled:
            bot.get_command(command).enabled = False
            await ctx.send(f":ok_hand: The {command} command is now enabled, and can be used.")
        else:
            await ctx.send(f"The {command} command is already enabled!")


# Error catching
@bot.event
async def on_command_error(ctx, exception):
    """Catches exceptions raised during usage of the bot"""
    if exception == commands.errors.CommandNotFound:  # Ignore invalid commands
        pass
    else:
        try:
            await ctx.send(
                ":warning: **An error occurred.** This error has been logged, please notify a bot admin if necessary.\n"
                f"\nError details: ```{exception}```")
        except Exception as criticalexception:
            print("An error occurred, attempt to report error as a message failed.")
            print(criticalexception)
        finally:
            print(f"Error: {exception}")


# Run the bot!
print("Initialising session...")

if __name__ == "__main__":
    try:
        bot.run(env.DISCORDTOKEN)
    except Exception as error:
        if str(error).startswith("Cannot connect to host"):
            print("Error: Network connection failed. Is Discord down or inaccessible? Is there an internet connection?")

        elif str(error) == "Improper token has been passed.":
            print("Error: Invalid token. Please check if the environment variable \"env.DISCORDTOKEN\" is valid.")

        else:
            print("Error: Uncaught exception during bot initialisation.")

        print(f"Error details:\n{error}")

print("Session ended.")
