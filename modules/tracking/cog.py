from __future__ import annotations
import typing 

if typing.TYPE_CHECKING:
    from client.client import Client

import discord 

from discord import app_commands 
from discord.ext import commands 

import setup as s

from modules.tracking import classes

class TrackingCog(app_commands.Group, commands.Cog):
    def __init__(self, client : Client):
        self.client = client

        super().__init__(name="summary", description="Summarise tracking module")
    
    @app_commands.command(name="user", description="Get the tracking summary of a user")
    @app_commands.describe(user="A user to get the tracking summary for (defaults to yourself)")
    async def _user_command(self, ctx : discord.Interaction | commands.Context, user : discord.Member = None):

        if "tracking" not in await self.client.data.get_modules(ctx.guild):
            return await self.client.send(ctx, "Module `tracking` not enabled in this server.")

        author = user or (ctx.user if isinstance(ctx, discord.Interaction) else ctx.author)
        guild = classes.Guild(self.client, "all_time")
        user = await guild.get_user(author.id)

        embed = discord.Embed(title=f"User summary of {author}", color=s.embed)

        

        embed.add_field(name="Statuses", value=f"""
Online: **{classes.generate_time(user.types.online.total_time)}** [{user.types.online.last_seen.timestamp}]
Do Not Disturb: **{classes.generate_time(user.types.dnd.total_time)}** [{user.types.dnd.last_seen.timestamp}]
Idle: **{classes.generate_time(user.types.idle.total_time)}** [{user.types.idle.last_seen.timestamp}]
Offline: **{classes.generate_time(user.types.offline.total_time)}** [{user.types.offline.last_seen.timestamp}]
        """)

        embed.add_field(name="More", value=f"""
Online : Idle : Offline - **{classes.ratioFunction(user.types.online.total_time + user.types.dnd.total_time, user.types.idle.total_time, user.types.offline.total_time)}**
        """, inline=False)
        
        if isinstance(ctx, discord.Interaction):
            return await ctx.response.send_message(embed=embed)
            
        return await ctx.reply(embed=embed, mention_author=False)

async def setup(bot : commands.Bot):
    await bot.add_cog(TrackingCog(bot.client), guild=s.slash_guild)