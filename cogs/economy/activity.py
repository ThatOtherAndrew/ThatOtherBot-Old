import aiosqlite
import asyncio
from discord.ext import commands


class Activity(commands.Cog):
    def __init__(self, bot):
        async def dbconnect():
            db = await aiosqlite.connect("assets/db/economy.db")
            await db.execute("""
                CREATE TABLE IF NOT EXISTS currency (
                    guildID int,
                    userID int,
                    currency int,
                    PRIMARY KEY (guildID, userID)
                )
            """)
            return db

        self.bot = bot
        self.db = asyncio.run(dbconnect())

    @commands.Cog.listener()
    async def on_messasge(self):
        pass


def setup(bot):
    bot.add_cog(Activity(bot))
