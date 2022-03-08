import discord 
from discord.ext import commands
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

class BridgeInteraction():

    def __init__(self, bot : commands.Bot, command : app_commands.Command, message : discord.Message):
        self.command = command 
        self.bot = bot 
        self.message = message

        self.response = BridgeResponse(self)

class BridgeResponse():

    def __init__(self, bridge : BridgeInteraction):
        self.bridge = bridge

    async def send_message(self, content=None):
        await self.bridge.message.reply(content=content, mention_author=False)


    


async def parse_message(bot : commands.Bot, tree : app_commands.CommandTree, message : discord.Message):
    commands = tree.get_commands(guild=setup.slash_guild)

    prefix = await bot.get_prefix(message)

    for command in commands:
        if message.content.lower().startswith(prefix.lower() + command.name.lower()):

            await command.callback(BridgeInteraction(bot, command, message))