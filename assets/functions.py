import discord
import json
import munch
import os
import sys
from dotenv import load_dotenv
from glob import glob
from traceback import format_exception
import colorama as colour

colour.init(autoreset=True)


def loadjson(file) -> munch.Munch:
    """Attempts to load a JSON file and returns it as a Munch object"""
    try:
        with open(f"{file}.json", "r") as f:
            return munch.munchify(json.loads(f.read()))
    except SyntaxError:
        print("Error: Reading config.json file. Is the config.json file valid syntax?")
        sys.exit()
    except FileNotFoundError:
        print("Error: Locating config.json file. Is the config.json file present in the same directory as this script?")
        sys.exit()


def savejson(obj, file) -> None:
    """Takes a Munch object in and writes it to a file as JSON"""
    try:
        with open(f"{file}.json", "w") as f:
            f.write(json.dumps(munch.unmunchify(obj), indent=2))
            f.truncate()
    except FileNotFoundError:
        print("Error: Locating config.json file. Is the config.json file present in the same directory as this script?")
        sys.exit()


def loadenv() -> munch.Munch:
    """Loads the environment variables and returns it as a Munch object"""
    load_dotenv()
    return munch.munchify(os.environ)


config = loadjson("config")
env = loadenv()


def formatexception(exception: Exception) -> str:
    exception = "".join(format_exception(type(exception), exception, exception.__traceback__)).rstrip()
    return f"[X] " + exception.replace('\n', '\n │  ')


def getextensions(searchdir: str = "") -> list:
    if searchdir.startswith("cogs."):
        searchdir = searchdir[5:]
    if os.path.isfile(f"cogs/{searchdir.replace('.', '/')}.py"):
        return [f"cogs.{searchdir}"]
    else:
        extensionpaths = [i.replace("\\", ".").replace("/", ".")[:-3] for i in glob(
            f"cogs/{searchdir.replace('.', '/')}/**/*.py",
            recursive=True
        )]
        return extensionpaths if extensionpaths != [] else [None]


def initembed(ctx, title, description="", image=None, bordercolour=config.embed.colour):
    embed = discord.Embed(title=title, description=description, color=bordercolour)
    embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar_url)
    if image is not None:
        img = discord.File(f"assets/img/{image}.png", filename=f"{image}.png")
        embed.set_thumbnail(url=f"attachment://{image}.png")
        return munch.munchify({"embed": embed, "file": img})
    else:
        return embed


async def reporterror(ctx, exception) -> None:
    try:
        formattedexception = formatexception(exception).replace("\n │  ", "\n").replace("```", "`‍`‍`")[4:][-1018:]
        e = initembed(ctx, "An error occurred during execution", bordercolour=0xFF0000)
        e.add_field(name="Traceback (May be truncated)", value=f"```{formattedexception}```")
        await ctx.send(embed=e)
    except Exception as criticalerror:
        print(f"{colour.Fore.RED}{colour.Style.BRIGHT}[X] An error occurred, "
              f"attempt to report error as a message failed\n{formatexception(criticalerror)}")
    finally:
        print(f"{colour.Fore.RED}{formatexception(exception)}")


# def splitflags(inputargs: list, inputflags: list) -> (list, munch.Munch):
#     args = []
#     flags = {}
#     doubleflag = None
#     for arg in inputargs:
#         if doubleflag:
#             flags[doubleflag] = arg
#             doubleflag = None
#         elif re.match(r"^-[^-]+$", arg):
#             flags[arg[1:]] = True
#         elif re.match(r"^--[^-]+$", arg):
#             doubleflag = arg[2:]
#         else:
#             args.append(arg)
#
#     return args, munch.munchify(flags)
