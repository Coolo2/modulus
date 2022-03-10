from client.client import Client 

from client import version, bridge

from discord.ext import commands
from discord import app_commands
import discord 
import setup
from web import web
import os

from discord.ext import tasks



intents = discord.Intents.default()
intents.message_content = True

async def get_prefix(bot : commands.Bot, message : discord.Message):

    prefix = await client.data.get_prefix(message.guild)
    return commands.when_mentioned_or(prefix, prefix.upper(), prefix.capitalize())(bot, message)


bot = commands.Bot(command_prefix=get_prefix, intents=intents)
client = Client(bot)

tree = app_commands.CommandTree(bot)
extensions = [file.replace(".py", "") for file in os.listdir('./cogs') if file.endswith(".py")]

bot.tree = tree
bot.client = client 

refresh_commands = False

@bot.event 
async def on_connect():
    await bot.client.file.initialise_databases()

@bot.event 
async def on_ready():


    guild = bot.get_guild(450914634963353600)
    user = await bot.fetch_user(368071242189897728)

    print(await client.data.get_logs(guild))

    await bot.change_presence(activity=discord.Activity(name=f"/help | v{version.versions[0].name}", type=discord.ActivityType.playing))
    print(f"{bot.user} online.")

    regular_task.start()

    quart_app = await web.generate_app(bot, client)

    bot.loop.create_task(quart_app.run_task(host=setup.host, port=setup.port))

    await bridge.sync(bot, tree, refresh_commands)

@tasks.loop(seconds=60 if setup.production else 15)
async def regular_task():
    await bot.client.file.sync_databases()

for extension in extensions:
    bot.load_extension(f"cogs.{extension}")

bot.run(setup.env("token"))