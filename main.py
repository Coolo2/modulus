from client.client import Client 

from discord.ext import commands
from discord import app_commands
import discord 
import setup
import os

import modules.tracking.overwrites
from web import web
from client import version, bridge

from discord import Client as DisClient
from discord.ext import tasks

intents = discord.Intents.all()

async def get_prefix(bot : commands.Bot, message : discord.Message):

    prefix = await client.data.get_prefix(message.guild)
    return commands.when_mentioned_or(prefix, prefix.upper(), prefix.capitalize())(bot, message)


bot : DisClient | commands.Bot = commands.Bot(command_prefix=get_prefix, intents=intents, case_insensitive=True)
client = Client(bot)

tree : app_commands.CommandTree = bot.tree


bot.client = client 

refresh_commands = False

@bot.event 
async def on_connect():
    await client.file.initialise_databases()

@bot.event 
async def on_ready():

    await bot.change_presence(activity=discord.Activity(name=f"/help | v{version.versions[0].name}", type=discord.ActivityType.playing))
    print(f"{bot.user} online.")

    regular_task.start()

    quart_app = await web.generate_app(bot, client)

    bot.loop.create_task(quart_app.run_task(host=setup.host, port=setup.port))

    await bridge.sync(bot, tree, refresh_commands)

@tasks.loop(seconds=client.loop_seconds)
async def regular_task():
    await client.file.sync_databases()

    await modules.tracking.overwrites.task(client)

extensions = [file.replace(".py", "") for file in os.listdir('./cogs') if file.endswith(".py")]

async def setup_hook():
    for extension in extensions:
        await bot.load_extension(f"cogs.{extension}")

    for module in client.moduleNames:
        try:
            await bot.load_extension(f"modules.{module}.cog")

            print("Loaded", module)
        except Exception as e:
            print("Extension not loaded: " + str(e))

bot.setup_hook = setup_hook

bot.run(setup.env("token"))