import re
import subprocess
import discord
from discord.ext import commands


class Events(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot = bot
        self.isSpeak = False
        self.voice_client = None
        self.channel = None
        self.queue = []

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:
            return

        if not self.isSpeak:
            return

        if message.channel.id != self.channel:
            return

        prefix = await self.bot.get_prefix(message)
        content = re.sub(
                "https?://[\w!\?/\+\-_~=;\.,\*&@#\$%\(\)'\[\]]+",
                "",
                message.content
                ).replace("\n", "")

        isCommand = False

        for command in self.bot.commands:
            command_name = f"{prefix}{command.name}"
            name_result = re.match(command_name, content)

            if name_result is not None:
                isCommand = True
                break

            for aliase in command.aliases:
                aliase_name = f"{prefix}{aliase}"
                aliase_result = re.match(aliase_name, content)

                if aliase_result is not None:
                    isCommand = True
                    break

        if isCommand:
            return

        self.queue.append(content)
        self.bot.dispatch("speaking")

    @commands.command(name="yomiage", aliases=["start", "s"])
    async def start(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("ボイスチャンネルに接続してください")
            return

        try:
            await ctx.author.voice.channel.connect()
        except Exception as e:
            print(e)
            return

        self.isSpeak = True
        self.voice_client = ctx.guild.voice_client
        self.channel = ctx.channel.id
        await ctx.send("接続しました")

    @commands.command(name="usero", aliases=["end", "e"])
    async def end(self, ctx):
        if ctx.guild.voice_client is None:
            await ctx.send("接続していません")
            return

        try:
            await ctx.guild.voice_client.disconnect()
        except Exception as e:
            print(e)
            return

        self.isSpeak = False
        self.voice_client = None
        self.channel = None
        self.queue = []
        await ctx.send("切断しました")

    @start.error
    async def start_error(self, ctx, error):
        print(error)

    @end.error
    async def end_error(self, ctx, error):
        print(error)

    @commands.Cog.listener()
    async def on_speaking(self):
        while True:
            length = len(self.queue)
            if length <= 0:
                break

            if self.voice_client.is_playing():
                continue

            content = self.queue[0]

            if content == "":
                self.queue.pop(0)
                continue

            subprocess.run(
                    [
                        "open_jtalk",
                        "-m",
                        "/usr/share/hts-voice/nitech-jp-atr503-m001/nitech_jp_atr503_m001.htsvoice",
                        "-x",
                        "/var/lib/mecab/dic/open-jtalk/naist-jdic",
                        "-ow",
                        "/tmp/wav.opus"
                    ],
                    input=content,
                    shell=False,
                    text=True
                    )

            try:
                self.voice_client.play(discord.FFmpegPCMAudio("/tmp/wav.opus"))
            except Exception as e:
                print(e)

            self.queue.pop(0)

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx):
        self.bot.dispatch("reload")
        await ctx.send("Reload completed!")

    @reload.error
    async def reload_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            return
        print(error)

def setup(bot):
    bot.add_cog(Events(bot))
