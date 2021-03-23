import discord
import json
import munch
import os
import sys
from dotenv import load_dotenv
from traceback import format_exception
import colorama as colour

colour.init(autoreset=True)


def loadjson(file):
    """Attempts to load a JSON file and returns it as a Munch() object"""
    try:
        with open(f"{file}.json", "r") as f:
            return munch.munchify(json.loads(f.read()))
    except SyntaxError:
        print("Error: Reading config.json file. Is the config.json file valid syntax?")
        sys.exit()
    except FileNotFoundError:
        print("Error: Locating config.json file. Is the config.json file present in the same directory as this script?")
        sys.exit()


def savejson(obj, file):
    """Takes a Munch() object in and writes it to a file as JSON"""
    try:
        with open(f"{file}.json", "w") as f:
            f.write(json.dumps(munch.unmunchify(obj), indent=2))
            f.truncate()
    except FileNotFoundError:
        print("Error: Locating config.json file. Is the config.json file present in the same directory as this script?")
        sys.exit()


def loadenv():
    """Loads the environment variables and returns it as a Munch() object"""
    load_dotenv()
    return munch.munchify(os.environ)


config = loadjson("config")
env = loadenv()


def formatexception(exception: Exception):
    exception = "".join(format_exception(type(exception), exception, exception.__traceback__)).rstrip()
    return f"[X] " + exception.replace('\n', '\n │  ')


def getextensions(searchdir: str = ""):
    extensions = []
    for path, _, files in os.walk(f".\\cogs\\{searchdir}"):
        for file in files:
            if file.endswith(".py"):
                extensions.append(f"{path[2:].replace(chr(92), '.')}.{file[:-3]}")
    return extensions if extensions != [] else None


def initembed(ctx, title, description="", image=None, bordercolour=config.embed.colour):
    embed = discord.Embed(title=title, description=description, color=bordercolour)
    embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar_url)
    if image is not None:
        img = discord.File(f"assets/img/{image}.png", filename=f"{image}.png")
        embed.set_thumbnail(url=f"attachment://{image}.png")
        return munch.munchify({"embed": embed, "file": img})
    else:
        return embed


async def reporterror(ctx, exception):
    try:
        e = initembed(ctx, "An error occurred during execution", bordercolour=0xFF0000)
        e.add_field(
            name="Traceback (May be truncated):",
            value=f"```{formatexception(exception).replace('```', '`‍`‍`')[-1018:]}```"
        )
        await ctx.send(embed=e)
    except Exception as criticalerror:
        print(f"{colour.Fore.RED}{colour.Style.BRIGHT}[X] An error occurred, "
              f"attempt to report error as a message failed\n{formatexception(criticalerror)}")
    finally:
        print(f"{colour.Fore.RED}{formatexception(exception)}")
