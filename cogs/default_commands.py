from __future__ import annotations
import typing 

if typing.TYPE_CHECKING:
    from client.client import Client

import discord 

from discord.ext import commands 
from discord import app_commands 

import setup as s 

from client import errors, lang

class HelpCommandView(discord.ui.View):
    def __init__(self, ctx : discord.Interaction | commands.Context):

        super().__init__(timeout=500)
        la = lang.get(ctx).g

        self.add_item(discord.ui.Button(style=discord.ButtonStyle.url, label=la().view_commands, emoji="📃", url=f"{s.address}/commands"))

class DefaultCommands(commands.Cog):
    def __init__(self, client : Client):
        self.client = client 
    
    @app_commands.command(name=lang.en().help, description=lang.en().help_description)
    async def _help(self, ctx : discord.Interaction | commands.Context):

        la = lang.get(ctx).g
        
        embed = discord.Embed(title=la().bot_help, description=f"{la().description} {la().owned_description}", color=s.embed)
        embed.add_field(name=la().commands, value=la().use_button)

        await self.client.send(ctx, embed=embed, view=HelpCommandView(ctx))

async def setup(bot : commands.Bot):
    await bot.add_cog(DefaultCommands(bot.client), guild=s.slash_guild)