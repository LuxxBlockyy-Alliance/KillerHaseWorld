from asyncio import run
import discord
from discord.ext import tasks
import asyncio  # Janosch hat das await vergessen
import requests
import os

import source.api
from source import tools, globalchat
from rich.console import Console
import sys

console = Console()

console.print("[[bold green]+[/bold green]] > Checking if Database exists")
if not os.path.exists("./source/world.db"):
    console.print("[[bold yellow]![/bold yellow]] > Creating new database")
    asyncio.run(tools.create_database("./source/world.db"))
    console.print("[[bold yellow]![/bold yellow]] > Creating new database table")
    asyncio.run(tools.create_table("./source/world.db", "world_chats", "id, channel_id, webhook_url, guild_id, guild_invite"))

try:
    bot = discord.Bot(intents=discord.Intents.all())
except RuntimeError as e:
    console.print("[[bold yellow]![/bold yellow]] > Closing session")
    sys.exit(0)


async def get_server_count():
    return int(len(bot.guilds))

@bot.event
async def on_ready():
    console.print(f"[[bold green]+[/bold green]] > Bot Started Successfully with username {bot.user}")
    await bot.change_presence(activity=discord.Game(name=f" mit {await get_server_count()} Servern"))
    update_presence.start()


@tasks.loop(minutes=3)
async def update_presence():
    await bot.change_presence(activity=discord.Game(name=f" mit {await get_server_count()} Servern"))


console.print("[[bold green]+[/bold green]] > Setting up Bot Cogs")
bot.load_extension("source.globalchat")

console.print("[[bold green]+[/bold green]] > Access file to get Token")
bot.run(run(tools.get_DC_token()))
