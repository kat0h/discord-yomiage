import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load Discord Api Token
load_dotenv()

cogs = [
    "cogs.error",
    "cogs.events"
]


class Yomiage(commands.Bot):

    def __init__(self, prefix) -> None:
        intents = discord.Intents.default()
        super().__init__(
            command_prefix=prefix,
            intents=intents,
            # help_command=None,
            case_insensitive=True
        )

        for cog in cogs:
            try:
                self.load_extension(cog)
            except Exception as e:
                print(e)

    async def on_ready(self):
        print(f"Login success as {self.user.name}")
        # await self.change_presence(activity=discord.Game(
        # name="!yomiage", type=1))

    @commands.Cog.listener()
    async def on_reload(self):
        for cog in cogs:
            try:
                self.reload_extension(cog)
            except Exception as e:
                print(e)

def run():
    bot = Yomiage(prefix="!")

    try:
        TOKEN = os.environ["DISCORD_BOT_TOKEN"]
    except KeyError:
        print("Token is not found")
    except Exception as e:
        print(e)

    try:
        bot.run(TOKEN)
    except discord.errors.LoginFailure:
        print("Invalid Token")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    run()
