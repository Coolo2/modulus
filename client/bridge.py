import discord 
from discord.ext import commands
from discord.ext.commands import core
from discord import app_commands

import setup

class BridgeCommand():

    def __init__(self, func):
        self.func = func 
        
    
    def run(self):
        
        return self.func()

def bridge_command(func, **kwargs):

    cmd = BridgeCommand(func)

    cmd.run()
    
async def sync(bot : commands.Bot, tree : app_commands.CommandTree, refresh_commands : bool):
    
    commands = tree.get_commands(guild=setup.slash_guild)

    for command in commands:

        cmd = core.Command(command.callback)
        cmd.name = command.name 
        cmd.description = command.description
        
        bot.add_command(cmd)

    if refresh_commands:
        await tree.sync(guild=setup.slash_guild)