import os
import discord
import subprocess
from dotenv import load_dotenv

# Load Discord Api Token
load_dotenv()
DISCORD_KEY = os.getenv('DISCORD_BOT_TOKEN')
if DISCORD_KEY is None:
    exit(1)

client = discord.Client()
global speakQueue
speakQueue = []
global isSpeak
isSpeak = False
global channel
channel = ""

@client.event
async def on_ready():
    print("Login success")

@client.event
async def on_message(message):
    global isSpeak
    global speakQueue
    global channel

    if message.author.bot:
        return

    if message.content == "!yomiage":
        if message.author.voice is None:
            await message.channel.send("ボイスチャンネルに接続してください")
            return
        await message.author.voice.channel.connect()
        isSpeak = True
        channel = message.channel.id
        await message.channel.send("接続しました")
    elif message.content == "!usero":
        if message.guild.voice_client is None:
            await message.channel.send("接続していません")
            return
        await message.guild.voice_client.disconnect()
        isSpeak = False
        await message.channel.send("切断しました")
    else:
        if isSpeak and message.channel.id == channel:
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
                    input=message.content,
                    shell=False,
                    text=True
                    )
            message.guild.voice_client.play(
                    discord.FFmpegPCMAudio("/tmp/wav.opus"))

client.run(DISCORD_KEY)