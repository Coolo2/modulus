from client import fileclient, httpclient, dataclient

import os
import setup

from discord.ext import commands
from discord import Client as Cl

import discord

class Client():

    def __init__(self, bot : commands.Bot | Cl):
        
        self.bot = bot
        self.moduleNames = [name for name in os.listdir("modules") if os.path.isdir(os.path.join("modules", name))]
        self.loop_seconds = 60 if setup.production else 15
        
        self.http = httpclient.HTTP(self)

        self.file = fileclient.FileClient(self)

        self.data = dataclient.DataClient(self)
    
    async def send(self, ctx : discord.Interaction | commands.Context, content = None, embed = None):


        if isinstance(ctx, discord.Interaction):
            return await ctx.response.send_message(content=content, embed=embed)
            
        return await ctx.reply(content=content, embed=embed, mention_author=False)
        