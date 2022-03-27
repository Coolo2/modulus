from __future__ import annotations
import typing 

if typing.TYPE_CHECKING:
    from client.client import Client

import discord 

from discord.ext import commands 
from discord import app_commands 

import setup as s 

from client import errors

class ErrorHandling(commands.Cog):
    def __init__(self, client : Client):
        self.client = client 
    
        @self.client.bot.event
        async def on_command_error(
                ctx : commands.Context | discord.Interaction, 
                error : app_commands.errors.CommandInvokeError | commands.CommandInvokeError, 
                command = None
        ):
            
            command : commands.Command | app_commands.Command = command or ctx.command 
            author : discord.Member = ctx.user if isinstance(ctx, discord.Interaction) else ctx.author

            embed = discord.Embed(
                title="You've run into an unknown error",
                description=f"```{error}```",
                color=s.embedFail
            )

            if isinstance(error.original, errors.MildError):
                embed = discord.Embed(
                    title=error.original.title,
                    description=error.original.description,
                    color=s.embedFail
                )

            await self.client.send(ctx, embed=embed, ephemeral=True)

        async def on_error(interaction : discord.Interaction, command : app_commands.Command, error : Exception):
            
            await on_command_error(interaction, error, command)
        
        self.client.bot.tree.error(on_error)

async def setup(bot : commands.Bot):
    await bot.add_cog(ErrorHandling(bot.client), guild=s.slash_guild)