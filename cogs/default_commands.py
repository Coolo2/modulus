from __future__ import annotations
import typing 

if typing.TYPE_CHECKING:
    from client.client import Client

import discord 

from discord.ext import commands 
from discord import app_commands 

import setup as s 

from client import errors

class HelpCommandView(discord.ui.View):
    def __init__(self):

        super().__init__(timeout=500)

        self.add_item(discord.ui.Button(style=discord.ButtonStyle.url, label="View Commands", emoji="📃", url=f"{s.address}/commands"))

class DefaultCommands(commands.Cog):
    def __init__(self, client : Client):
        self.client = client 
    
    @app_commands.command(name="help", description="Get help for the bot and list its commands")
    async def _help(self, ctx : discord.Interaction | commands.Context):
        
        embed = discord.Embed(title="Bot help", description=f"{s.description} It is owned by **Coolo2#5499** and was released on XXXX", color=s.embed)

        embed.add_field(name="Commands", value="Use the button below to see the bot's commands")

        await self.client.send(ctx, embed=embed, view=HelpCommandView())

async def setup(bot : commands.Bot):
    await bot.add_cog(DefaultCommands(bot.client), guild=s.slash_guild)