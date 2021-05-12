import discord
import json
import munch
import os
from dotenv import load_dotenv
from glob import glob
from traceback import format_exception
import colorama as colour


colour.init(autoreset=True)


def loadjson(file: str) -> munch.Munch:
    """Attempts to load a JSON file and returns it as a Munch object"""
    with open(f"{file.replace('.', '/')}.json", "r") as f:
        return munch.munchify(json.loads(f.read()))


def savejson(obj: munch.Munch, file: str) -> None:
    """Takes a Munch object in and writes it to a file as JSON"""
    with open(f"{file.replace('.', '/')}.json", "w") as f:
        f.write(json.dumps(munch.unmunchify(obj), indent=2))
        f.truncate()


def loadenv() -> munch.Munch:
    """Loads the environment variables and returns it as a Munch object"""
    load_dotenv()
    return munch.munchify(os.environ)


config = loadjson("config")
env = loadenv()


def formatexception(exception: Exception, indent: bool = False) -> str:
    exception = "".join(format_exception(type(exception), exception, exception.__traceback__)).rstrip()
    if not config.debug:
        exception = exception.split("\n\nThe above exception was the direct cause of the following exception:\n\n")[0]
    return (f"[X] " + exception.replace('\n', '\n │  ')) if indent else exception


def getextensions(searchdir: str = "") -> list:
    if searchdir.startswith("cogs."):
        searchdir = searchdir[5:]
    if os.path.isfile(f"cogs/{searchdir.replace('.', '/')}.py"):
        return [f"cogs.{searchdir}"]
    extensionpaths = [i.replace("\\", ".").replace("/", ".")[:-3] for i in glob(
        f"cogs/{searchdir.replace('.', '/')}/**/*.py",
        recursive=True
    )]
    return extensionpaths if extensionpaths != [] else [None]


def initembed(ctx, title, description="", image=None, bordercolour=config.embed.colour):
    embed = discord.Embed(title=title, description=description, color=bordercolour)
    embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar_url)
    if image is None:
        return embed
    img = discord.File(f"assets/img/{image}.png", filename=f"{image}.png")
    embed.set_thumbnail(url=f"attachment://{image}.png")
    return munch.munchify({"embed": embed, "file": img})


def plaintext(inputstr: str, truncatelength: int = None) -> str:
    cleanstr = inputstr.replace('``', '`‌`').replace('``', '`‌`')
    if truncatelength is None:
        return f"``‌{cleanstr}‌``"

    if len(cleanstr) <= truncatelength - 6:
        return f"``‌{cleanstr}‌``"
    else:
        return f"``‌{cleanstr[:truncatelength - 8]}...``"


async def reporterror(ctx, exception) -> None:
    try:
        formattedexception = formatexception(exception).replace("```", "`‌`‌`")[-1018:]
        e = initembed(ctx, "An error occurred during execution", bordercolour=0xFF0000)
        e.add_field(name="Traceback (May be truncated)", value=f"```{formattedexception}```")
        await ctx.send(embed=e)
    except Exception as criticalerror:
        print(f"{colour.Fore.RED}{colour.Style.BRIGHT}[X] An error occurred, "
              f"attempt to report error as a message failed\n │  {criticalerror}")
    finally:
        print(f"{colour.Fore.YELLOW}[!] {ctx.author} ({ctx.author.id}) ran the command "
              f"{colour.Style.BRIGHT}{ctx.message.content}{colour.Style.NORMAL}, resulting in the following error:")
        print(f"{colour.Fore.RED}{formatexception(exception, indent=True)}")


class Flags:
    class Flag:
        def __init__(self, flag: str, hasparameter: bool, defaultparametervalue, casesensitive: bool) -> None:
            self.name = flag
            self.id = flag if casesensitive else flag.lower()
            self.hasparameter = hasparameter
            self.defaultvalue = defaultparametervalue if hasparameter else None
            self.casesensitive = casesensitive

    def __init__(self, inputargs) -> None:
        self.inputargs = inputargs
        self.inputflags = []

    def addflag(self, flag: str, hasparameter: bool = False, defaultvalue=None, casesensitive: bool = False) -> None:
        """Add a flag to be parsed. Set hasparameter to True to use a flag with a parameter"""
        self.inputflags.append(self.Flag(flag, hasparameter, defaultvalue, casesensitive))

    def splitflags(self) -> tuple[list, dict]:
        """Returns a list of non-flag arguments and a Munch object of flags and their parameters"""
        inputargs = self.inputargs
        splitflags = {}

        for flag in self.inputflags:
            buffer = []
            if not flag.hasparameter:
                for arg in inputargs:
                    if flag.id == (arg if flag.casesensitive else arg.lower()):
                        splitflags[flag.name] = True
                    else:
                        buffer.append(arg)
            else:
                splitflags[flag.name] = flag.defaultvalue
                getparameter = False
                for arg in inputargs:
                    if getparameter:
                        try:
                            splitflags[flag.name] = arg if flag.defaultvalue is None else type(flag.defaultvalue)(arg)
                        except ValueError:
                            pass
                        getparameter = False
                    elif flag.id == (arg if flag.casesensitive else arg.lower()):
                        getparameter = True
                    elif (arg if flag.casesensitive else arg.lower()).startswith(f"{flag.id}="):
                        if flag.defaultvalue is None:
                            splitflags[flag.name] = arg.split("=", 1)[1]
                        else:
                            try:
                                splitflags[flag.name] = type(flag.defaultvalue)(arg.split("=", 1)[1])
                            except ValueError:
                                pass
                    else:
                        buffer.append(arg)
            inputargs = buffer
        return inputargs, splitflags
