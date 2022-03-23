import discord 
from discord.ext import commands
from discord.ext.commands import core
from discord import app_commands

import setup
    
async def group_empty_cor(ctx : commands.context.Context):
    
    if ctx.invoked_subcommand is None:
        await ctx.send(f'Invalid subcommand pased. Try using `/{ctx.command.name}`')

async def sync(bot : commands.Bot, tree : app_commands.CommandTree, refresh_commands : bool):

    commands = tree.get_commands(guild=setup.slash_guild)

    for command in commands:
        if hasattr(command, "commands"):
            # is group 

            gr = core.Group(name=command.name, func=group_empty_cor)

            for command_child in command.commands:

                cmd = core.Command(command_child.callback)

                cmd.cog = command_child.binding

                cmd.name = command_child.name
                cmd.description = command_child.description
                
                gr.add_command(cmd)

            bot.add_command(gr)
        else:

            # is normal slash command
            
            cmd = core.Command(command.callback)

            cmd.cog = command.binding

            cmd.name = command.name
            cmd.description = command.description
            
            bot.add_command(cmd)

    if refresh_commands:
        await tree.sync(guild=setup.slash_guild)