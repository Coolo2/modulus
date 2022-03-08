from client.client import Client 

from client import version, bridge

from discord.ext import commands
from discord import app_commands
import discord 
import setup
from web import web

from discord.ext import tasks

client = Client()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot("!", intents=intents)
tree = app_commands.CommandTree(bot)

bot.tree = tree
bot.client = client 

refresh_commands = False

@tree.command(name="test", description="test command", guild=setup.slash_guild)
async def _test_command(interaction):

    return await interaction.response.send_message("hi")

@bot.event 
async def on_connect():
    await bot.client.file.initialise_databases()

@bot.event 
async def on_ready():
    await bot.change_presence(activity=discord.Activity(name=f"/help | v{version.versions[0].name}", type=discord.ActivityType.playing))
    print(f"{bot.user} online.")

    regular_task.start()

    quart_app = await web.generate_app(bot)

    bot.loop.create_task(quart_app.run_task(host=setup.host, port=setup.port))

    if refresh_commands:
        await tree.sync(guild=setup.slash_guild)

@bot.event 
async def on_message(message : discord.Message):
    await bridge.parse_message(bot, bot.tree, message)

@tasks.loop(seconds=60)
async def regular_task():
    await bot.client.file.sync_databases()

bot.run(setup.env("token"))