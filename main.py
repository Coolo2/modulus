from client.client import Client 

from client import version

import discord 
import setup
from web import web

from discord.ext import tasks

client = Client()

intents = discord.Intents.default()

bot = discord.Bot()
bot.client = client 

@bot.event 
async def on_connect():
    await bot.client.file.initialise_databases()

@bot.event 
async def on_ready():
    await bot.change_presence(activity=discord.Activity(name=f"/help | v{version.versions[0].name}", type=discord.ActivityType.playing))
    print(f"{bot.user} online.")

    regular_task.start()

    quart_app = await web.generate_app(bot)

    bot.loop.create_task(quart_app.run_task(host="0.0.0.0", port=5000))

    await bot.sync_commands()

@tasks.loop(seconds=60)
async def regular_task():
    await bot.client.file.sync_databases()

bot.run(setup.env("token"))