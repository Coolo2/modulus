from client import fileclient, httpclient, dataclient

import os
import setup as s

from discord.ext import commands
from discord import Client as Cl

import discord
from discord import app_commands

class Client():

    def __init__(self, bot : commands.Bot | Cl):
        
        self.bot = bot
        self.tree : app_commands.CommandTree = self.bot.tree 

        self.moduleNames = [name for name in os.listdir("modules") if os.path.isdir(os.path.join("modules", name))]
        self.loop_seconds = 60 if s.production else 15
        
        self.http = httpclient.HTTP(self)

        self.file = fileclient.FileClient(self)

        self.data = dataclient.DataClient(self)
    
    async def send(self, ctx : discord.Interaction | commands.Context, content = None, embed = None, view=None, ephemeral=False):


        if isinstance(ctx, discord.Interaction):
            return await ctx.response.send_message(content=content, embed=embed, view=view, ephemeral=ephemeral)
            
        return await ctx.reply(content=content, embed=embed, view=view, mention_author=False)
    
    def get_command(self, command_name : str) -> app_commands.Command:

        for command in self.tree.walk_commands(guild=s.slash_guild):

            if not hasattr(command, "_children"):
                command_name_it = ""

                if command.parent:
                    command_name_it = f"{command.parent.name} {command.name}"
                else:
                    command_name_it = command.name

                if command_name_it == command_name:
                    return command 
        
        return None
        