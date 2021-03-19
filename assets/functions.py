import discord
import json
import munch
import os
import re
import sys
from dotenv import load_dotenv


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


def initembed(ctx, title, description="", image=None, colour=config.embed.colour):
    embed = discord.Embed(title=title, description=description, color=colour)
    embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar_url)
    if image is not None:
        img = discord.File(f"assets/img/{image}.png", filename=f"{image}.png")
        embed.set_thumbnail(url=f"attachment://{image}.png")
        return munch.munchify({"embed": embed, "file": img})
    else:
        return embed
