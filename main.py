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

refresh_commands = True

@tree.command(name="test", description="test command", guild=setup.slash_guild)
async def _test_command(ctx : discord.Interaction | commands.Context, arg : str):
    
    if isinstance(ctx, discord.Interaction):

        return await ctx.response.send_message(arg)
    else:

        return await ctx.reply(arg, mention_author=False)


@bot.event 
async def on_connect():
    await bot.client.file.initialise_databases()

@bot.event 
async def on_ready():
    g = bot.get_guild(450914634963353600)

    

    await bot.change_presence(activity=discord.Activity(name=f"/help | v{version.versions[0].name}", type=discord.ActivityType.playing))
    print(f"{bot.user} online.")

    regular_task.start()

    quart_app = await web.generate_app(bot, client)

    bot.loop.create_task(quart_app.run_task(host=setup.host, port=setup.port))

    await bridge.sync(bot, tree, refresh_commands)

timeframe = 60 if setup.production else 15

@tasks.loop(seconds=timeframe)
async def regular_task():
    await bot.client.file.sync_databases()

bot.run(setup.env("token"))